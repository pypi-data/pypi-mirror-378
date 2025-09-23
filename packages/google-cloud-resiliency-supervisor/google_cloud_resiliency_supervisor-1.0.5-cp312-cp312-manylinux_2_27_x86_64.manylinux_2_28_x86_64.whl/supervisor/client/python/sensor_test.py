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
from supervisor.client.python import sensor
from supervisor.client.python.test import constants
from supervisor.client.python.test import test_utils
import supervisor_core


class TestSensor:
  """Tests basic sensor python client functionality."""

  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mock_sensor_cls = mock.patch.object(
        supervisor_core, "Sensor", autospec=True
    ).start()
    self.mock_sensor_instance = self.mock_sensor_cls.return_value
    self.mock_sensor_instance.is_ready.return_value = True
    self.mock_sensor_instance.num_hosts.return_value = 5
    self.mock_sensor_instance.num_running_hosts.return_value = 2
    self.mock_sensor_instance.num_spare_hosts.return_value = 3
    self.mock_sensor_instance.is_complete.return_value = True

    self.config = test_utils.create_supervisor_config()
    self.sensor_instance = test_utils.create_sensor(self.config)
    self.sensor_instance._sensor = self.mock_sensor_instance  # pylint: disable=protected-access

  @pytest.fixture(autouse=True)
  def teardown_method(self):
    yield
    if self.sensor_instance:
      self.sensor_instance.shutdown()
    mock.patch.stopall()

  def test_sensor_start_stop(self):
    assert self.sensor_instance.name == "sensor"
    assert self.sensor_instance.address == f"localhost:{constants.SENSOR_PORT}"

    assert self.sensor_instance.num_hosts == 5
    assert self.sensor_instance.num_running_hosts == 2
    assert self.sensor_instance.num_spare_hosts == 3

    self.mock_sensor_instance.num_hosts.assert_called_once()
    self.mock_sensor_instance.num_running_hosts.assert_called_once()
    self.mock_sensor_instance.num_spare_hosts.assert_called_once()

  def test_sensor_wait_for_completion(self):
    self.sensor_instance.wait_for_completion()
    self.mock_sensor_instance.is_complete.assert_called()

  def test_sensor_repr(self):
    assert (
        repr(self.sensor_instance)
        == f"sensor@localhost:{constants.SENSOR_PORT}"
    )

  def test_sensor_no_supervisor_config(self):
    with mock.patch.object(
        supervisor_core.SupervisorConfig, "from_environment"
    ) as mock_from_environment:
      mock_from_environment.return_value = self.config
      mock_supervisor_client_cls = mock.patch.object(
          supervisor_core, "SupervisorClient"
      ).start()
      mock_supervisor_client_cls.return_value = self.config

      sensor_instance = sensor.Sensor(
          port=constants.SENSOR_PORT, num_grpc_threads=4
      )
      assert sensor_instance.name == "sensor"
      assert sensor_instance.address == f"localhost:{constants.SENSOR_PORT}"
      mock_from_environment.assert_called_once()


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
