"""Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import copy
import logging
import sys
from unittest import mock

from kubernetes import client
from kubernetes import config
import pytest
from supervisor.client.python.orchestrators import gke_callbacks
import supervisor_core


# pylint: disable=protected-access


class TestGkeCallbacks:
  """Tests basic GKE callbacks functionality."""

  @pytest.fixture(autouse=True)
  def setup_method(self):
    # Mock Kubernetes configuration loading
    self.mock_load_kube_config = mock.patch.object(
        config, "load_kube_config", autospec=True
    ).start()
    self.mock_load_incluster_config = mock.patch.object(
        config, "load_incluster_config", autospec=True
    ).start()

    # Mock subprocess
    self.mock_subprocess = mock.patch("subprocess.run", autospec=True).start()

    # Mock Kubernetes API
    self.mock_core_api = mock.patch.object(
        client, "CoreV1Api", autospec=True
    ).start()
    self.mock_custom_api = mock.patch.object(
        client, "CustomObjectsApi", autospec=True
    ).start()

    # Mock time.sleep
    self.mock_time_sleep = mock.patch("time.sleep", autospec=True).start()

    # Mock threading.Thread and watch.Watch to prevent actual threads/watches
    self.mock_thread_patcher = mock.patch("threading.Thread", autospec=True)
    self.mock_thread_class = self.mock_thread_patcher.start()
    self.mock_thread_class.side_effect = (
        lambda *args, **kwargs: mock.MagicMock()
    )
    self.mock_watch = mock.patch(
        "kubernetes.watch.Watch", autospec=True
    ).start()

    # Since __init__ starts threads, we need to mock API calls made within them
    self.mock_core_api.return_value.list_node.return_value = mock.MagicMock(
        items=[], metadata=mock.MagicMock(resource_version="1")
    )
    self.mock_core_api.return_value.list_namespaced_pod.return_value = (
        mock.MagicMock(items=[], metadata=mock.MagicMock(resource_version="1"))
    )

    # Create an instance of the KubernetesCallbacks class
    self.k8s_callbacks = gke_callbacks.KubernetesCallbacks(
        namespace="test-namespace"
    )
    self.k8s_callbacks.logger = logging.getLogger()
    self.k8s_callbacks.logger.setLevel(logging.INFO)

  @pytest.fixture(autouse=True)
  def teardown_method(self):
    yield
    # We need to manually call shutdown if threads were started
    if self.k8s_callbacks._cordon_watch_thread.start.called:
      self.k8s_callbacks.shutdown()
    mock.patch.stopall()

  def test_init(self):
    """Test that the __init__ method starts the watcher threads."""
    self.mock_thread_class.assert_has_calls([
        mock.call(target=self.k8s_callbacks._watch_cordoned_nodes),
        mock.call(target=self.k8s_callbacks._watch_all_pods),
    ])
    self.k8s_callbacks._cordon_watch_thread.start.assert_called_once()
    self.k8s_callbacks._pod_watch_thread.start.assert_called_once()

  def test_shutdown(self):
    """Test that the shutdown method stops all watcher threads."""
    # Simulate that the threads were started
    self.k8s_callbacks._cordon_watch_thread.start.called = True
    self.k8s_callbacks._pod_watch_thread.start.called = True

    self.k8s_callbacks.shutdown()

    assert self.k8s_callbacks._stop_cordon_watch.is_set()
    assert self.k8s_callbacks._stop_pod_watch.is_set()
    self.k8s_callbacks._cordon_watch_thread.join.assert_called_once()
    self.k8s_callbacks._pod_watch_thread.join.assert_called_once()

  def test_get_cordoned_nodes(self):
    """Test that get_cordoned_nodes returns the cached list."""
    self.k8s_callbacks._cordoned_nodes = {"node-1", "node-2"}
    assert set(self.k8s_callbacks.get_cordoned_nodes()) == {"node-1", "node-2"}
    # Ensure no API call is made beyond the initial one
    self.mock_core_api.return_value.list_node.assert_called_once()

  def test_poll_jobset_status_does_not_start_watcher(self):
    """Test that poll_jobset_status does not start a new watcher thread."""
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks._check_jobset_exists = mock.MagicMock(return_value=True)
    self.k8s_callbacks.jobset_pod_statuses["test-workload"] = {
        "all_running": True
    }

    # Reset the mock to see if it's called inside poll_jobset_status
    self.mock_thread_class.reset_mock()

    self.k8s_callbacks.poll_jobset_status(workload_info, "test-host")

    self.mock_thread_class.assert_not_called()

  def test_poll_jobset_status_all_running(self):
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks._check_jobset_exists = mock.MagicMock(return_value=True)
    self.k8s_callbacks.jobset_pod_statuses["test-workload"] = {
        "all_running": True
    }
    self.k8s_callbacks.workload_downtime["test-workload"] = 123.45

    self.k8s_callbacks.poll_jobset_status(workload_info, "test-host")

    assert self.k8s_callbacks.workload_downtime["test-workload"] is None
    self.mock_custom_api.return_value.delete_namespaced_custom_object.assert_not_called()

  def test_poll_jobset_status_not_all_running_under_threshold(self):
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    workload_info.workload_downtime_threshold_s = 60
    self.k8s_callbacks._check_jobset_exists = mock.MagicMock(return_value=True)
    self.k8s_callbacks.jobset_pod_statuses["test-workload"] = {
        "all_running": False,
        "pending_pods": ["pod-1"],
        "other_state_pods": [],
    }
    self.k8s_callbacks.workload_downtime["test-workload"] = None

    self.k8s_callbacks.poll_jobset_status(workload_info, "test-host")

    assert self.k8s_callbacks.workload_downtime["test-workload"] is not None
    self.mock_custom_api.return_value.delete_namespaced_custom_object.assert_not_called()

  @mock.patch("time.time")
  def test_poll_jobset_status_not_all_running_over_threshold(self, mock_time):
    mock_time.return_value = 100
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    workload_info.workload_downtime_threshold_s = 60
    self.k8s_callbacks._check_jobset_exists = mock.MagicMock(return_value=True)
    self.k8s_callbacks.jobset_pod_statuses["test-workload"] = {
        "all_running": False,
        "pending_pods": ["pod-1"],
        "other_state_pods": [],
    }
    self.k8s_callbacks.workload_downtime["test-workload"] = (
        10  # Started at t=10
    )

    # Mock the restart_jobset method to avoid its complex logic
    self.k8s_callbacks.restart_jobset = mock.MagicMock(return_value=True)

    self.k8s_callbacks.poll_jobset_status(workload_info, "test-host")

    self.k8s_callbacks.restart_jobset.assert_called_once_with(
        workload_info, "test-host"
    )
    assert self.k8s_callbacks.workload_downtime["test-workload"] is None

  @mock.patch("time.time")
  def test_poll_jobset_status_not_all_running_over_threshold_scale_down(
      self, mock_time
  ):
    mock_time.return_value = 100
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    workload_info.workload_downtime_threshold_s = 60
    workload_info.workload_scaling_enabled = True

    self.k8s_callbacks._check_jobset_exists = mock.MagicMock(return_value=True)
    self.k8s_callbacks.jobset_pod_statuses["test-workload"] = {
        "all_running": False,
        "pending_pods": ["pod-1"],
        "other_state_pods": [],
    }
    self.k8s_callbacks.workload_downtime["test-workload"] = (
        10  # Started at t=10
    )

    # Mock the restart_jobset and _delete_jobset method
    self.k8s_callbacks.restart_jobset = mock.MagicMock(return_value=True)
    self.k8s_callbacks._delete_jobset = mock.MagicMock(return_value=True)

    self.k8s_callbacks.poll_jobset_status(workload_info, "test-host")

    self.k8s_callbacks.restart_jobset.assert_called_once_with(
        workload_info, "test-host", "down", False
    )
    self.k8s_callbacks._delete_jobset.assert_not_called()
    assert self.k8s_callbacks.workload_downtime["test-workload"] is None

  def test_recalculate_jobset_pod_status(self):
    """Test the logic of recalculating pod statuses."""
    jobset_name = "test-jobset"
    mock_pod_running = mock.MagicMock(
        metadata=mock.MagicMock(name="pod-1"),
        status=mock.MagicMock(
            phase="Running",
            container_statuses=[
                mock.MagicMock(state=mock.MagicMock(running=True))
            ],
        ),
    )
    mock_pod_pending = mock.MagicMock(
        metadata=mock.MagicMock(name="pod-2"),
        status=mock.MagicMock(phase="Pending", start_time="some-time"),
    )
    mock_pod_failed = mock.MagicMock(
        metadata=mock.MagicMock(name="pod-3"),
        status=mock.MagicMock(phase="Failed"),
    )

    self.k8s_callbacks.jobset_pods[jobset_name] = {
        "pod-1": mock_pod_running,
        "pod-2": mock_pod_pending,
        "pod-3": mock_pod_failed,
    }

    self.k8s_callbacks._recalculate_jobset_pod_status(jobset_name)

    status = self.k8s_callbacks.jobset_pod_statuses[jobset_name]
    assert status["total_pods"] == 3
    assert status["running_pods"] == 1
    assert len(status["pending_pods"]) == 1
    assert len(status["other_state_pods"]) == 1
    assert not status["all_running"]

  def test_recalculate_jobset_pod_status_all_running(self):
    """Test the logic of recalculating pod statuses when all are running."""
    jobset_name = "test-jobset"
    mock_pod_running_1 = mock.MagicMock(
        metadata=mock.MagicMock(name="pod-1"),
        status=mock.MagicMock(
            phase="Running",
            container_statuses=[
                mock.MagicMock(state=mock.MagicMock(running=True))
            ],
        ),
    )
    mock_pod_running_2 = mock.MagicMock(
        metadata=mock.MagicMock(name="pod-2"),
        status=mock.MagicMock(
            phase="Running",
            container_statuses=[
                mock.MagicMock(state=mock.MagicMock(running=True))
            ],
        ),
    )

    self.k8s_callbacks.jobset_pods[jobset_name] = {
        "pod-1": mock_pod_running_1,
        "pod-2": mock_pod_running_2,
    }

    self.k8s_callbacks._recalculate_jobset_pod_status(jobset_name)

    status = self.k8s_callbacks.jobset_pod_statuses[jobset_name]
    assert status["total_pods"] == 2
    assert status["running_pods"] == 2
    assert not status["pending_pods"]
    assert not status["other_state_pods"]
    assert status["all_running"]

  def test_get_pod_on_host_found(self):
    daemon_pod_mock = mock.MagicMock(
        status=mock.MagicMock(phase="Running"),
    )
    daemon_pod_mock.metadata = mock.MagicMock()
    daemon_pod_mock.metadata.name = "test-pod-daemon"

    # Mock for "test-pod-other"
    other_pod_mock = mock.MagicMock(
        status=mock.MagicMock(phase="Running"),
    )
    other_pod_mock.metadata = mock.MagicMock()
    other_pod_mock.metadata.name = "test-pod-other"
    other_pod_mock.spec = mock.MagicMock(
        containers=[mock.MagicMock(resources=mock.MagicMock(limits={}))]
    )

    main_test_pod_mock = mock.MagicMock(
        status=mock.MagicMock(phase="Running"),
    )
    main_test_pod_mock.metadata = mock.MagicMock()
    main_test_pod_mock.metadata.name = "test-pod"
    main_test_pod_mock.spec = mock.MagicMock(
        containers=[
            mock.MagicMock(
                resources=mock.MagicMock(limits={"nvidia.com/gpu": "1"})
            )
        ]
    )

    self.mock_core_api.return_value.list_namespaced_pod.return_value = (
        mock.MagicMock(
            items=[
                daemon_pod_mock,
                other_pod_mock,
                main_test_pod_mock,
            ]
        )
    )
    pod_name = self.k8s_callbacks._get_pod_on_host("test-host")
    assert pod_name == "test-pod"

  def test_reset_host(self):
    # reset_host is currently a no-op, so just check it doesn"t raise an error
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks.reset_host(workload_info, "test-host")

  def test_drain_host(self):
    mock_pod = mock.MagicMock()
    mock_pod.metadata.name = "test-pod"
    self.k8s_callbacks._get_pod_on_host = mock.MagicMock(
        return_value="test-pod"
    )
    self.k8s_callbacks.cordon_host = mock.MagicMock()
    self.k8s_callbacks._force_delete_pod = mock.MagicMock()

    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks.drain_host(workload_info, "test-host")

    self.k8s_callbacks.cordon_host.assert_called_once_with(
        workload_info, "test-host"
    )
    self.k8s_callbacks._force_delete_pod.assert_called_once_with("test-pod")

  def test_cordon_host(self):
    self.mock_subprocess.return_value = mock.MagicMock(returncode=0)
    self.mock_core_api.return_value.read_node.return_value = mock.MagicMock(
        metadata=mock.MagicMock(labels={})
    )
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks.cordon_host(workload_info, "test-host")
    self.mock_subprocess.assert_called_once_with(
        ["kubectl", "cordon", "test-host"],
        check=True,
        capture_output=True,
        shell=False,
    )

  def test_cordon_host_pending_reboot(self):
    self.mock_core_api.return_value.read_node.return_value = mock.MagicMock(
        metadata=mock.MagicMock(
            labels={"cloud.google.com/perform-reboot": "true"}
        )
    )
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks.cordon_host(workload_info, "test-host")
    self.mock_subprocess.assert_not_called()

  def test_uncordon_host(self):
    self.mock_subprocess.return_value = mock.MagicMock(returncode=0)
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    self.k8s_callbacks.uncordon_host(workload_info, "test-host")
    self.mock_subprocess.assert_called_once_with(
        ["kubectl", "uncordon", "test-host"],
        check=True,
        capture_output=True,
        shell=False,
    )

  def test_delete_pod(self):
    self.k8s_callbacks._get_pod_on_host = mock.MagicMock(
        return_value="test-pod"
    )
    self.k8s_callbacks._force_delete_pod = mock.MagicMock()
    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"

    self.k8s_callbacks.delete_pod(workload_info, "test-host")

    self.k8s_callbacks._get_pod_on_host.assert_called_once_with("test-host")
    self.k8s_callbacks._force_delete_pod.assert_called_once_with("test-pod")

  def test_restart_jobset(self):
    mock_jobset_spec = {
        "metadata": {
            "name": "test-workload",
        },
        "spec": {
            "replicatedJobs": [{
                "name": "test-replicated-job",
                "template": {
                    "spec": {
                        "parallelism": 2,
                        "completions": 2,
                        "template": {
                            "metadata": {
                                "annotations": {
                                    "kueue.x-k8s.io/workload": "test-workload",
                                },
                            },
                            "spec": {
                                "containers": [{
                                    "name": "test-container",
                                    "env": [{"name": "NNODES", "value": "2"}],
                                }],
                            },
                        },
                    }
                },
            }]
        },
    }
    expected_jobset_spec = copy.deepcopy(mock_jobset_spec)
    expected_jobset_spec["spec"]["replicatedJobs"][0]["template"]["spec"][
        "template"
    ]["metadata"]["annotations"].pop("kueue.x-k8s.io/workload", None)

    self.k8s_callbacks._get_jobset_spec = mock.MagicMock(
        return_value=copy.deepcopy(mock_jobset_spec)
    )
    self.k8s_callbacks._delete_jobset = mock.MagicMock(return_value=True)
    self.k8s_callbacks._get_stuck_pods = mock.MagicMock(return_value=[])
    self.k8s_callbacks._create_jobset = mock.MagicMock(return_value=True)

    workload_info = supervisor_core.WorkloadInfo()
    workload_info.workload_name = "test-workload"
    workload_info.job_name = "test-replicated-job"
    workload_info.container_name = "test-container"
    workload_info.num_data_replicas = 2
    workload_info.max_num_data_replicas = 3
    workload_info.min_num_data_replicas = 1
    workload_info.num_nodes_per_data_replica = 1
    workload_info.container_termination_threshold_s = 10
    workload_info.workload_downtime_threshold_s = 10
    workload_info.max_in_job_restarts = 0
    workload_info.max_workload_restarts = 0
    workload_info.workload_scaling_enabled = False

    assert self.k8s_callbacks.restart_jobset(workload_info, "test-host")

    self.k8s_callbacks._get_jobset_spec.assert_called_once_with("test-workload")
    self.k8s_callbacks._delete_jobset.assert_called_once_with("test-workload")
    self.mock_time_sleep.assert_called_once_with(10)
    self.k8s_callbacks._get_stuck_pods.assert_called_once_with(workload_info)
    self.k8s_callbacks._create_jobset.assert_called_once_with(
        expected_jobset_spec
    )

  def test_get_workload_info(self):
    mock_jobset_spec = {
        "metadata": {
            "name": "test-workload",
            "annotations": {
                "supervisor/container-name": "test-container",
                "supervisor/job-name": "test-replicated-job",
                "supervisor/max-workload-restarts": "3",
                "supervisor/max-in-job-restarts": "0",
                "supervisor/workload-downtime-threshold-s": "180",
                "supervisor/enable-workload-scaling": "false",
                "supervisor/container-termination-threshold-s": "60",
                "supervisor/num-nodes-per-dp": "1",
                "supervisor/min-num-dp-replicas": "1",
                "supervisor/max-num-dp-replicas": "3",
            },
        },
        "spec": {
            "replicatedJobs": [{
                "name": "test-replicated-job",
                "template": {
                    "spec": {
                        "parallelism": 2,
                        "completions": 2,
                        "template": {
                            "metadata": {
                                "annotations": {
                                    "kueue.x-k8/workload": "test-workload",
                                },
                            },
                            "spec": {
                                "containers": [{
                                    "name": "test-container",
                                    "env": [{"name": "NNODES", "value": "2"}],
                                }],
                            },
                        },
                    }
                },
            }]
        },
    }
    self.mock_custom_api.return_value.list_namespaced_custom_object.return_value = {
        "items": [mock_jobset_spec]
    }
    self.k8s_callbacks._find_replicated_job_index = mock.MagicMock(
        return_value=0
    )
    self.k8s_callbacks._find_container_index = mock.MagicMock(return_value=0)
    self.k8s_callbacks._get_pod_on_host = mock.MagicMock(
        return_value="test-workload-0-0"
    )

    workload_info = self.k8s_callbacks.get_workload_info("test-host")
    assert workload_info.workload_name == "test-workload"
    assert workload_info.job_name == "test-replicated-job"
    assert workload_info.container_name == "test-container"
    assert workload_info.num_data_replicas == 2
    assert workload_info.max_num_data_replicas == 3
    assert workload_info.min_num_data_replicas == 1
    assert workload_info.num_nodes_per_data_replica == 1
    assert workload_info.container_termination_threshold_s == 60
    assert workload_info.workload_downtime_threshold_s == 180
    assert workload_info.max_in_job_restarts == 0
    assert workload_info.max_workload_restarts == 3
    assert not workload_info.workload_scaling_enabled


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
