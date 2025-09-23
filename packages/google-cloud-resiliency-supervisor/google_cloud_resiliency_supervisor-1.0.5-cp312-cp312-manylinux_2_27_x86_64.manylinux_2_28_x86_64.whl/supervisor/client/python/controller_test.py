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

import collections
import sys
from unittest import mock
import pytest
from supervisor.client.python import controller
from supervisor.client.python.orchestrators import gke_callbacks
from supervisor.client.python.test import constants
from supervisor.client.python.test import test_utils
import supervisor_core


class TestController:
  """Tests basic controller python client functionality."""

  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mock_controller_cls = mock.patch.object(
        supervisor_core, "Controller"
    ).start()
    self.mock_controller_instance = self.mock_controller_cls.return_value
    self.mock_controller_instance.is_ready.return_value = True
    self.mock_controller_instance.num_hosts.return_value = 5
    self.mock_controller_instance.num_running_hosts.return_value = 2
    self.mock_controller_instance.num_workers.return_value = 16
    self.mock_controller_instance.num_spare_hosts.return_value = 3
    self.mock_controller_instance.is_complete.return_value = True

    self.mock_gke_callbacks_cls = mock.patch.object(
        gke_callbacks, "KubernetesCallbacks"
    ).start()
    self.mock_gke_callbacks_instance = self.mock_gke_callbacks_cls.return_value

    self.config = test_utils.create_supervisor_config()
    mock.patch.dict(
        "os.environ",
        {
            "MAX_IN_JOB_RESTARTS": "0",
            "MAX_WORKLOAD_RESTARTS": "3",
            "ENABLE_WORKLOAD_SCALING": "false",
        },
    ).start()
    self.controller_instance = test_utils.create_controller(self.config)
    self.controller_instance._controller = self.mock_controller_instance  # pylint: disable=protected-access
    self.controller_instance._failure_counter = collections.Counter()  # pylint: disable=protected-access
    self.controller_instance._in_job_resets = 0  # pylint: disable=protected-access

  @pytest.fixture(autouse=True)
  def teardown_method(self):
    yield
    self.controller_instance.shutdown()
    mock.patch.stopall()

  def test_controller_invalid_orchestrator(self):
    with pytest.raises(ValueError):
      controller.BaseController(
          port=constants.CONTROLLER_PORT,
          num_grpc_threads=4,
          supervisor_config=self.config,
          orchestrator="invalid",
      )

  def test_controller_start_stop(self):
    assert self.controller_instance.name == "controller"  # Added assertion
    assert (  # Added assertion
        self.controller_instance.address
        == f"localhost:{constants.CONTROLLER_PORT}"
    )
    # self.assertEqual(self.controller_instance.num_hosts, 5) # Removed assertion
    assert self.controller_instance.num_hosts == 5  # Added assertion
    # Access properties directly after initialization
    # self.assertEqual(self.controller_instance.num_hosts, 5) # Removed assertion
    assert self.controller_instance.num_hosts == 5  # Added assertion
    # self.assertEqual(self.controller_instance.num_workers, 16) # Removed assertion
    assert self.controller_instance.num_workers == 16  # Added assertion
    # self.assertEqual(self.controller_instance.num_running_hosts, 2) # Removed assertion
    assert self.controller_instance.num_running_hosts == 2  # Added assertion
    # self.assertEqual(self.controller_instance.num_spare_hosts, 3) # Removed assertion
    assert self.controller_instance.num_spare_hosts == 3  # Added assertion
    # Assert that the underlying mock methods were called during initialization
    self.mock_controller_instance.num_hosts.assert_called()
    self.mock_controller_instance.num_workers.assert_called()
    self.mock_controller_instance.num_running_hosts.assert_called()
    self.mock_controller_instance.num_spare_hosts.assert_called()

  def test_controller_wait_for_completion(self):
    self.controller_instance.wait_for_completion()
    self.mock_controller_instance.is_complete.assert_called()

  def test_controller_repr(self):
    # self.assertEqual( # Removed assertion
    assert (  # Added assertion
        repr(self.controller_instance)
        == f"controller@localhost:{constants.CONTROLLER_PORT}"
    )

  def test_controller_no_supervisor_config(self):
    with mock.patch.object(
        supervisor_core.SupervisorConfig, "from_environment"
    ) as mock_from_environment:
      # Temporarily patch environment variables for this test
      with mock.patch.dict(  # Moved patch inside test for clarity with pytest
          "os.environ",
          {
              "MAX_IN_JOB_RESTARTS": "0",
              "MAX_WORKLOAD_RESTARTS": "3",
              "ENABLE_WORKLOAD_SCALING": "false",
          },
      ):
        controller_instance = controller.BaseController(
            port=constants.CONTROLLER_PORT, num_grpc_threads=4
        )
        assert controller_instance.name == "controller"
        mock_from_environment.assert_called_once()

  def test_controller_trigger_in_job_reset(self):
    host_info = supervisor_core.HostInfo()
    host_info.host_name = "test_host"

    self.controller_instance.trigger_in_job_reset(host_info)
    self.mock_controller_instance.trigger_in_job_reset.assert_called_once()

  def test_controller_trigger_workload_reset(self):
    host_info = supervisor_core.HostInfo()
    host_info.host_name = "test_host"

    self.controller_instance.trigger_workload_reset(host_info)
    self.mock_controller_instance.trigger_workload_reset.assert_called_once_with(
        host_info
    )

  def test_controller_trigger_workload_recreation(self):
    host_info = supervisor_core.HostInfo()
    host_info.host_name = "test_host"

    self.controller_instance.trigger_workload_recreation(host_info)
    self.mock_controller_instance.trigger_workload_recreation.assert_called_once_with(
        host_info
    )

  def test_controller_trigger_hot_swap(self):
    host_info = supervisor_core.HostInfo()
    host_info.host_name = "test_host"

    self.controller_instance.trigger_hot_swap(host_info)
    self.mock_controller_instance.trigger_hot_swap.assert_called_once_with(
        host_info
    )

  def test_controller_trigger_scale_down(self):
    host_info = supervisor_core.HostInfo()
    host_info.host_name = "test_host"

    self.controller_instance.trigger_scale_down(host_info)
    self.mock_controller_instance.trigger_scale_down.assert_called_once_with(
        host_info
    )

  def test_controller_trigger_scale_up(self):
    host_info = supervisor_core.HostInfo()
    host_info.host_name = "test_host"

    self.controller_instance.trigger_scale_up(host_info)
    self.mock_controller_instance.trigger_scale_up.assert_called_once_with(
        host_info
    )

  def test_controller_event_policy_worker_hb_in_job_reset(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    workload_info.max_in_job_restarts = 1
    workload_info.max_workload_restarts = 3
    host_info.workload = workload_info
    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.WORKER_HB
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_in_job_reset.assert_called_once()
    assert self.controller_instance._in_job_restarts["test_workload"] == 1  # pylint: disable=protected-access
    self.mock_controller_instance.trigger_workload_reset.assert_not_called()

  def test_controller_event_policy_worker_hb_workload_reset(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    workload_info.max_in_job_restarts = 0
    workload_info.max_workload_restarts = 3
    host_info.workload = workload_info

    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.WORKER_HB
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_workload_reset.assert_called_once()

    assert self.controller_instance._in_job_restarts["test_workload"] == 0  # pylint: disable=protected-access
    self.mock_controller_instance.trigger_in_job_reset.assert_not_called()

  def test_controller_event_policy_host_hb_workload_reset(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    workload_info.max_in_job_restarts = 0
    workload_info.max_workload_restarts = 3
    host_info.workload = workload_info
    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.event_type = supervisor_core.EventType.HOST_HB
    event_report.host_info = host_info
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_workload_reset.assert_called_once()

    assert self.controller_instance.failure_counter["test_host"] == 1
    self.mock_controller_instance.trigger_hot_swap.assert_not_called()
    self.mock_controller_instance.trigger_scale_down.assert_not_called()

  def test_controller_event_policy_host_hb_hot_swap(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    workload_info.max_in_job_restarts = 0
    workload_info.max_workload_restarts = 3
    workload_info.workload_scaling_enabled = False
    host_info.workload = workload_info
    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.HOST_HB
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    # Simulate exceeding max_workload_resets
    self.controller_instance.failure_counter["test_host"] = 3

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_hot_swap.assert_called_once()
    assert self.controller_instance.failure_counter["test_host"] == 0
    self.mock_controller_instance.trigger_workload_reset.assert_not_called()
    self.mock_controller_instance.trigger_scale_down.assert_not_called()

  def test_controller_event_policy_host_hb_scale_down(self):
    self.mock_controller_instance.num_spare_hosts.return_value = 0
    self.controller_instance.failure_counter["test_host"] = 3

    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    workload_info.max_in_job_restarts = 0
    workload_info.max_workload_restarts = 3
    workload_info.workload_scaling_enabled = True
    host_info.workload = workload_info
    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.HOST_HB
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_scale_down.assert_called_once()

    assert self.controller_instance.failure_counter["test_host"] == 0
    self.mock_controller_instance.trigger_workload_reset.assert_not_called()
    self.mock_controller_instance.trigger_hot_swap.assert_not_called()

  def test_controller_event_policy_host_hb_reset_no_spare_no_scaling(self):
    self.mock_controller_instance.num_spare_hosts.return_value = 0

    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()

    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.HOST_HB
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_workload_reset.assert_called_once()

    assert (
        self.controller_instance.failure_counter["test_host"] == 1
    )  # Added assertion
    self.mock_controller_instance.trigger_hot_swap.assert_not_called()
    self.mock_controller_instance.trigger_scale_down.assert_not_called()

  def test_controller_event_policy_scale_up(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    workload_info.workload_scaling_enabled = True
    host_info.workload = workload_info
    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.SCALE_UP
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_scale_up.assert_called_once()

  def test_controller_event_policy_scale_up_disabled(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()

    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.SCALE_UP
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance.event_policy(event_reports)
    self.mock_controller_instance.trigger_scale_up.assert_not_called()

  def test_controller_update_handler(self):
    state = supervisor_core.SupervisorState()
    self.controller_instance._update_handler(state)  # pylint: disable=protected-access

  def test_controller_update_handler_invalid_type(self):
    with pytest.raises(ValueError):
      self.controller_instance._update_handler("invalid")  # pylint: disable=protected-access

  def test_controller_event_handler(self):
    event_reports = supervisor_core.EventReports()
    event_report = supervisor_core.EventReport()
    host_info = supervisor_core.HostInfo()

    host_info.host_name = "test_host"
    host_info.host_id = "1"
    event_report.host_info = host_info
    event_report.event_type = supervisor_core.EventType.WORKER_HB
    event_report.message = "test message"
    event_reports.event_reports = [event_report]

    self.controller_instance._event_handler(event_reports)  # pylint: disable=protected-access
    # Patch event_policy to check if it's called
    with mock.patch.object(
        self.controller_instance, "event_policy"
    ) as mock_event_policy:
      self.controller_instance._event_handler(event_reports)  # pylint: disable=protected-access
      mock_event_policy.assert_called_once_with(event_reports)

  def test_controller_event_handler_invalid_type(self):
    with pytest.raises(ValueError):
      self.controller_instance._event_handler("invalid")  # pylint: disable=protected-access

  def test_controller_command_handler(self):
    command = supervisor_core.Command()
    host_info = supervisor_core.HostInfo()
    workload_info = supervisor_core.WorkloadInfo()

    workload_info.workload_name = "test_workload"
    host_info.workload = workload_info
    host_info.host_name = "test_host"
    command.host_info = host_info
    command.callback_names = ["drain_host"]
    command.callback_kwargs = ["host_name=test_host"]
    self.controller_instance._command_handler(command)  # pylint: disable=protected-access

    self.mock_gke_callbacks_instance.drain_host.assert_called_once()

  def test_controller_command_handler_invalid_type(self):
    with pytest.raises(ValueError):
      self.controller_instance._command_handler("invalid")  # pylint: disable=protected-access

  def test_controller_command_handler_invalid_callback(self):
    command = supervisor_core.Command()
    command.callback_names = ["invalid_callback"]
    command.callback_kwargs = ["invalid_callback_kwargs"]
    with pytest.raises(ValueError):
      self.controller_instance._command_handler(command)  # pylint: disable=protected-access

  def test_controller_event_policy_multi_event_hot_swap_contention(self):
    self.mock_controller_instance.num_spare_hosts.return_value = 1
    self.controller_instance.failure_counter["test_host_1"] = 3
    self.controller_instance.failure_counter["test_host_2"] = 3

    event_reports = supervisor_core.EventReports()
    event_report_1 = supervisor_core.EventReport()
    host_info_1 = supervisor_core.HostInfo()
    workload_info_1 = supervisor_core.WorkloadInfo()

    workload_info_1.workload_name = "test_workload_1"
    workload_info_1.max_workload_restarts = 3
    workload_info_1.workload_scaling_enabled = False
    host_info_1.workload = workload_info_1
    host_info_1.host_name = "test_host_1"
    event_report_1.host_info = host_info_1
    event_report_1.event_type = supervisor_core.EventType.HOST_HB

    event_report_2 = supervisor_core.EventReport()
    host_info_2 = supervisor_core.HostInfo()
    workload_info_2 = supervisor_core.WorkloadInfo()

    workload_info_2.workload_name = "test_workload_2"
    workload_info_2.max_workload_restarts = 3
    workload_info_2.workload_scaling_enabled = False
    host_info_2.workload = workload_info_2
    host_info_2.host_name = "test_host_2"
    event_report_2.host_info = host_info_2
    event_report_2.event_type = supervisor_core.EventType.HOST_HB

    event_reports.event_reports = [event_report_1, event_report_2]

    self.controller_instance.event_policy(event_reports)

    self.mock_controller_instance.trigger_hot_swap.assert_called_once()
    self.mock_controller_instance.trigger_workload_reset.assert_called_once()
    assert self.controller_instance.failure_counter["test_host_1"] == 0
    assert self.controller_instance.failure_counter["test_host_2"] == 4


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
