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
from unittest import mock

import pytest
from supervisor.client.python import actuator
from supervisor.client.python.test import constants
from supervisor.client.python.test import test_utils
import supervisor_core


class TestActuator:
  """Tests basic actuator python client functionality."""

  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mock_actuator_cls = mock.patch.object(
        supervisor_core, "Actuator"
    ).start()
    self.mock_actuator_instance = self.mock_actuator_cls.return_value
    self.mock_actuator_instance.is_ready.return_value = True
    self.mock_actuator_instance.num_hosts.return_value = 5
    self.mock_actuator_instance.num_running_hosts.return_value = 2
    self.mock_actuator_instance.num_spare_hosts.return_value = 3
    self.mock_actuator_instance.is_complete.return_value = True

    self.config = test_utils.create_supervisor_config()
    self.actuator_instance = test_utils.create_actuator(self.config)
    self.actuator_instance._actuator = self.mock_actuator_instance  # pylint: disable=protected-access

  @pytest.fixture(autouse=True)
  def teardown_method(self):
    yield
    self.actuator_instance.shutdown()
    mock.patch.stopall()

  def test_actuator_start_stop(self):
    assert self.actuator_instance.name == "actuator"
    assert (
        self.actuator_instance.address == f"localhost:{constants.ACTUATOR_PORT}"
    )

    assert self.actuator_instance.num_hosts == 5
    assert self.actuator_instance.num_running_hosts == 2
    assert self.actuator_instance.num_spare_hosts == 3

    self.mock_actuator_instance.num_hosts.assert_called_once()
    self.mock_actuator_instance.num_running_hosts.assert_called_once()
    self.mock_actuator_instance.num_spare_hosts.assert_called_once()

  def test_actuator_wait_for_completion(self):
    self.actuator_instance.wait_for_completion()
    self.mock_actuator_instance.is_complete.assert_called()

  def test_actuator_repr(self):
    assert (
        repr(self.actuator_instance)
        == f"actuator@localhost:{constants.ACTUATOR_PORT}"
    )

  def test_actuator_no_supervisor_config(self):
    with mock.patch.object(
        supervisor_core.SupervisorConfig, "from_environment"
    ) as mock_from_environment:
      mock_from_environment.return_value = self.config
      with mock.patch.object(
          supervisor_core, "SupervisorClient"
      ) as mock_supervisor_client_cls:
        mock_supervisor_client_cls.return_value = self.config

        actuator_instance = actuator.Actuator(
            port=constants.ACTUATOR_PORT, num_grpc_threads=4
        )
        assert actuator_instance.name == "actuator"
        assert (
            actuator_instance.address == f"localhost:{constants.ACTUATOR_PORT}"
        )
        mock_from_environment.assert_called_once()


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
