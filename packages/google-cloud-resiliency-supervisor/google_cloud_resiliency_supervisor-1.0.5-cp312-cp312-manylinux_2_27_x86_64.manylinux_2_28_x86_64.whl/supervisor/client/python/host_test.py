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

import sys
import threading
from unittest import mock
import pytest
from supervisor.client.python import host
from supervisor.client.python import utils
from supervisor.client.python.orchestrators import gke_callbacks
from supervisor.client.python.test import constants
from supervisor.client.python.test import test_utils
from supervisor.core.python import device_info
from supervisor.watchdogs.python import ecc_watchdog
from supervisor.watchdogs.python import xid_watchdog
import supervisor_core


class TestHost:
  """Unit tests for the Host Supervisor Python client class."""

  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mock_host_cls = mock.patch.object(
        supervisor_core, "Host", autospec=True
    ).start()
    self.mock_host_instance = self.mock_host_cls.return_value
    self.mock_host_instance.is_ready.return_value = True
    self.mock_host_instance.is_complete.return_value = True
    self.mock_host_instance.is_cordoned.return_value = False
    self.mock_host_instance.num_workers.return_value = 2
    self.mock_host_instance.export_info.return_value = supervisor_core.HostInfo(
        host_name="test-host-name",
        host_id="test-host-id",
        host_address=f"127.0.0.1:{constants.HOST_PORT}",
        zone="test-zone-1a",
        superblock_id="sb1",
        subblock_id="rack2",
        host_serial_number="serial3",
        state=supervisor_core.DeviceState.RUNNING,
    )

    self.mock_get_host_name = mock.patch.object(
        utils, "get_host_name", autospec=True
    ).start()
    self.mock_get_host_id = mock.patch.object(
        utils, "get_host_id", autospec=True
    ).start()
    self.mock_get_host_ip = mock.patch.object(
        utils, "get_host_ip", autospec=True
    ).start()
    self.mock_get_host_zone = mock.patch.object(
        utils, "get_host_zone", autospec=True
    ).start()
    self.mock_get_host_physical_attributes = mock.patch.object(
        utils, "get_host_physical_attributes", autospec=True
    ).start()
    self.mock_check_and_clean_port = mock.patch.object(
        utils, "check_and_clean_port", autospec=True
    ).start()
    self.mock_clean_termination_files = mock.patch.object(
        utils, "clean_termination_files", autospec=True
    ).start()
    self.mock_create_termination_file = mock.patch.object(
        utils, "create_termination_file", autospec=True
    ).start()
    self.mock_is_host_running_workload = mock.patch.object(
        utils, "is_host_running_workload", autospec=True
    ).start()
    self.mock_ecc_watchdog = mock.patch.object(
        ecc_watchdog, "ECCWatchdog", autospec=True
    ).start()
    self.mock_xid_watchdog = mock.patch.object(
        xid_watchdog, "XIDWatchdog", autospec=True
    ).start()
    self.mock_gke_callbacks = mock.patch.object(
        gke_callbacks, "KubernetesCallbacks", autospec=True
    ).start()

    self.mock_get_host_name.return_value = "test-host-name"
    self.mock_get_host_id.return_value = "test-host-id"
    self.mock_get_host_ip.return_value = "127.0.0.1"
    self.mock_get_host_zone.return_value = "test-zone-1a"
    self.mock_get_host_physical_attributes.return_value = (
        "sb1",
        "rack2",
        "serial3",
    )
    self.mock_is_host_running_workload.return_value = True
    self.mock_gke_callbacks.return_value.get_workload_info.return_value = (
        supervisor_core.WorkloadInfo(
            workload_name="test-workload",
            max_workload_restarts=3,
            max_in_job_restarts=0,
            workload_scaling_enabled=False,
            workload_downtime_threshold_s=180,
            container_termination_threshold_s=60,
            num_data_replicas=1,
            max_num_data_replicas=1,
            min_num_data_replicas=1,
            num_nodes_per_data_replica=1,
            job_name="test-job",
            container_name="test-container",
        )
    )

    self.config = test_utils.create_supervisor_config()
    self.host_instance = None

  @pytest.fixture(autouse=True)
  def teardown_method(self):
    yield
    if self.host_instance:
      self.host_instance.shutdown()
    mock.patch.stopall()

  def test_init_success_topology_aware(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        enable_topology_aware_scheduling=True,
    )

    self.mock_get_host_name.assert_called_once()
    self.mock_get_host_id.assert_called_once()
    self.mock_get_host_ip.assert_called_once()
    self.mock_get_host_zone.assert_called_once()
    self.mock_get_host_physical_attributes.assert_called_once()
    self.mock_check_and_clean_port.assert_called_once_with(constants.HOST_PORT)
    self.mock_clean_termination_files.assert_called_once()
    self.mock_host_cls.assert_called_once()

    assert self.host_instance.project == "test-project"
    assert self.host_instance.port == constants.HOST_PORT
    assert self.host_instance.host_id == "test-host-id"
    assert self.host_instance.host_serial_number == "serial3"
    assert self.host_instance.host_name == "test-host-name"
    assert self.host_instance.host_address == f"127.0.0.1:{constants.HOST_PORT}"
    assert self.host_instance.num_workers == 2
    assert self.host_instance.zone == "test-zone-1a"
    assert self.host_instance.max_workers_per_host == 8

  def test_init_success_no_topology_aware(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        enable_topology_aware_scheduling=False,
    )

    self.mock_get_host_physical_attributes.assert_not_called()
    self.mock_host_cls.assert_called_once()

  def test_init_with_address(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        address="my-address",
        supervisor_config=self.config,
    )
    self.mock_get_host_ip.assert_not_called()
    assert (
        self.host_instance.host_address == f"my-address:{constants.HOST_PORT}"
    )
    assert self.host_instance.max_workers_per_host == 8

  def test_init_with_custom_workers(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        workers_per_host=4,
        supervisor_config=self.config,
    )
    assert self.host_instance.max_workers_per_host == 4

  def test_init_with_watchdogs(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        watchdogs=["ecc", "xid"],
    )
    self.mock_ecc_watchdog.assert_called_once()
    self.mock_xid_watchdog.assert_called_once()
    assert "ecc" in self.host_instance._watchdogs  # pylint: disable=protected-access
    assert "xid" in self.host_instance._watchdogs  # pylint: disable=protected-access

  def test_init_invalid_watchdog(self):
    with pytest.raises(ValueError, match="Invalid watchdog"):
      self.host_instance = host.Host(
          project_id="test-project",
          port=constants.HOST_PORT,
          supervisor_config=self.config,
          watchdogs=["invalid"],
      )

  def test_init_no_supervisor_config(self):
    with mock.patch.object(
        supervisor_core.SupervisorConfig, "from_environment"
    ) as mock_from_environment:
      mock_from_environment.return_value = self.config
      self.host_instance = host.Host(
          project_id="test-project",
          port=constants.HOST_PORT,
      )
      mock_from_environment.assert_called_once()
      assert self.host_instance.max_workers_per_host == 8

  def test_start_heartbeat(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
    )
    self.host_instance.start_heartbeat()
    assert self.host_instance.max_workers_per_host == 8
    self.mock_host_instance.start_heartbeat.assert_called_once()

  def test_await_completion_no_watchdogs(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        watchdogs=None,
    )
    self.host_instance.await_completion()
    assert self.host_instance.max_workers_per_host == 8
    self.mock_host_instance.is_complete.assert_called()
    self.mock_ecc_watchdog.return_value.poll.assert_not_called()
    self.mock_xid_watchdog.return_value.poll.assert_not_called()

  def test_await_completion_with_watchdogs(self):
    mock_ecc_instance = self.mock_ecc_watchdog.return_value
    mock_xid_instance = self.mock_xid_watchdog.return_value
    mock_ecc_instance.poll.return_value = [
        supervisor_core.EventReport(
            event_type=supervisor_core.EventType.ECC,
            message="ECC Error",
        )
    ]
    mock_xid_instance.poll.return_value = []
    self.mock_host_instance.is_complete.side_effect = [False, False, True]

    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        watchdogs=["ecc", "xid"],
        watchdog_check_interval_s=1,
    )
    # Run await_completion in a separate thread
    thread = threading.Thread(target=self.host_instance.await_completion)
    thread.start()
    thread.join(timeout=5)  # Wait for the thread to complete with a timeout

    self.mock_host_instance.is_complete.assert_called()
    mock_ecc_instance.poll.assert_called()
    mock_xid_instance.poll.assert_called()
    self.mock_host_instance.report_event.assert_called()

  def test_await_completion_not_running(self):
    self.mock_host_instance.export_info.return_value = supervisor_core.HostInfo(
        state=supervisor_core.DeviceState.SPARE
    )
    mock_ecc_instance = self.mock_ecc_watchdog.return_value
    mock_xid_instance = self.mock_xid_watchdog.return_value

    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        watchdogs=["ecc", "xid"],
    )
    self.host_instance.await_completion()
    assert self.host_instance.max_workers_per_host == 8
    self.mock_host_instance.is_complete.assert_called()
    mock_ecc_instance.poll.assert_not_called()
    mock_xid_instance.poll.assert_not_called()

  def test_await_completion_standalone_mode(self):
    self.mock_host_instance.export_info.return_value = supervisor_core.HostInfo(
        state=supervisor_core.DeviceState.SPARE
    )
    mock_ecc_instance = self.mock_ecc_watchdog.return_value
    mock_xid_instance = self.mock_xid_watchdog.return_value
    mock_ecc_instance.poll.return_value = [
        supervisor_core.EventReport(
            event_type=supervisor_core.EventType.ECC,
            message="ECC Error",
        )
    ]
    mock_xid_instance.poll.return_value = []
    self.mock_host_instance.is_complete.side_effect = [False, False, True]
    self.mock_host_instance.num_workers.return_value = 0

    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        enable_standalone_mode=True,
        watchdogs=["ecc", "xid"],
        watchdog_check_interval_s=1,
    )

    # Run await_completion in a separate thread
    thread = threading.Thread(target=self.host_instance.await_completion)
    thread.start()
    thread.join(timeout=5)  # Wait for the thread to complete with a timeout

    self.mock_host_instance.is_complete.assert_called()
    mock_ecc_instance.poll.assert_called()
    mock_xid_instance.poll.assert_called()
    self.mock_host_instance.report_event.assert_called()

  def test_await_completion_standalone_mode_cordoned(self):
    self.mock_host_instance.export_info.return_value = supervisor_core.HostInfo(
        state=supervisor_core.DeviceState.SPARE
    )
    self.mock_host_instance.is_cordoned.return_value = True
    mock_ecc_instance = self.mock_ecc_watchdog.return_value
    mock_xid_instance = self.mock_xid_watchdog.return_value
    mock_ecc_instance.poll.return_value = [
        supervisor_core.EventReport(
            event_type=supervisor_core.EventType.ECC,
            message="ECC Error",
        )
    ]
    mock_xid_instance.poll.return_value = []
    self.mock_host_instance.is_complete.side_effect = [False, False, True]
    self.mock_host_instance.num_workers.return_value = 0

    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        enable_standalone_mode=True,
        watchdogs=["ecc", "xid"],
        watchdog_check_interval_s=1,
    )

    # Run await_completion in a separate thread
    thread = threading.Thread(target=self.host_instance.await_completion)
    thread.start()
    thread.join(timeout=5)  # Wait for the thread to complete with a timeout

    self.mock_host_instance.is_complete.assert_called()
    mock_ecc_instance.poll.assert_not_called()
    mock_xid_instance.poll.assert_not_called()
    self.mock_host_instance.report_event.assert_not_called()

    assert self.host_instance.state == device_info.DeviceState.FAILED

  def test_shutdown(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
    )
    self.host_instance.shutdown()
    self.mock_host_instance.shutdown.assert_called_once()
    self.mock_create_termination_file.assert_called_once()

  def test_report_event(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
    )
    event_reports = [
        supervisor_core.EventReport(
            event_type=supervisor_core.EventType.ECC,
            message="Test Error",
        )
    ]
    self.host_instance.report_event(event_reports)
    self.mock_host_instance.report_event.assert_called_once()

  def test_export_info(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        enable_topology_aware_scheduling=True,
    )
    exported_info = self.host_instance.export_info()
    assert isinstance(exported_info, supervisor_core.HostInfo)
    assert exported_info.host_name == "test-host-name"
    assert exported_info.host_id == "test-host-id"
    assert exported_info.host_address == f"127.0.0.1:{constants.HOST_PORT}"
    assert exported_info.zone == "test-zone-1a"
    assert exported_info.superblock_id == "sb1"
    assert exported_info.subblock_id == "rack2"
    assert exported_info.host_serial_number == "serial3"

  def test_update_info(self):
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
    )
    new_info = supervisor_core.HostInfo(host_name="new-host-name")
    self.host_instance.update_info(new_info)
    assert self.host_instance.max_workers_per_host == 8
    # Host name should not be updated.
    assert self.host_instance.host_info.host_name == "test-host-name"

  def test_init_physical_attributes_none(self):
    self.mock_get_host_physical_attributes.return_value = ("", "", "")
    self.host_instance = host.Host(
        project_id="test-project",
        port=constants.HOST_PORT,
        supervisor_config=self.config,
        enable_topology_aware_scheduling=True,
    )
    self.mock_get_host_physical_attributes.assert_called_once()
    assert not self.host_instance.host_info.superblock_id
    assert not self.host_instance.host_info.subblock_id
    assert not self.host_instance.host_info.host_serial_number

  def test_init_invalid_workers_per_host(self):
    with pytest.raises(
        ValueError, match="workers_per_host must be a positive integer"
    ):
      self.host_instance = host.Host(
          project_id="test-project",
          port=constants.HOST_PORT,
          supervisor_config=self.config,
          workers_per_host=0,
      )


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
