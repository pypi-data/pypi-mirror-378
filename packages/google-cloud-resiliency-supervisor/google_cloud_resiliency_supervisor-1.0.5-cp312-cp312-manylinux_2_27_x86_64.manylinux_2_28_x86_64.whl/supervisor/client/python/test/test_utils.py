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

import os

from supervisor.client.python import actuator
from supervisor.client.python import controller
from supervisor.client.python import host
from supervisor.client.python import sensor
from supervisor.client.python.test import constants
import supervisor_core


def create_supervisor_config() -> supervisor_core.SupervisorConfig:
  """Creates a SupervisorConfig instance."""
  os.environ["SENSOR_ADDRESS"] = f"localhost:{constants.SENSOR_PORT}"
  os.environ["ACTUATOR_ADDRESS"] = f"localhost:{constants.ACTUATOR_PORT}"
  os.environ["CONTROLLER_ADDRESS"] = f"localhost:{constants.CONTROLLER_PORT}"

  os.environ["HEARTBEAT_POLLING_PERIOD_S"] = "2"
  os.environ["HEARTBEAT_TIMEOUT_S"] = "5"
  os.environ["WORKLOAD_NAMESPACE"] = "default"

  supervisor_config = supervisor_core.SupervisorConfig.from_environment()

  for var_name in [
      "SENSOR_ADDRESS",
      "ACTUATOR_ADDRESS",
      "CONTROLLER_ADDRESS",
      "HEARTBEAT_POLLING_PERIOD_S",
      "HEARTBEAT_TIMEOUT_S",
      "WORKLOAD_NAMESPACE",
  ]:
    del os.environ[var_name]

  return supervisor_config


def create_actuator(
    config: supervisor_core.SupervisorConfig,
) -> actuator.Actuator:
  """Creates an instance of the Actuator pybind wrapper."""
  actuator_instance = actuator.Actuator(
      port=constants.ACTUATOR_PORT,
      num_grpc_threads=4,
      supervisor_config=config,
  )
  return actuator_instance


def create_controller(
    config: supervisor_core.SupervisorConfig,
) -> controller.BaseController:
  """Creates an instance of the Controller pybind wrapper."""
  controller_instance = controller.BaseController(
      port=constants.CONTROLLER_PORT,
      num_grpc_threads=4,
      supervisor_config=config,
  )
  return controller_instance


def create_sensor(
    config: supervisor_core.SupervisorConfig,
) -> sensor.Sensor:
  """Creates an instance of the Sensor pybind wrapper."""
  sensor_instance = sensor.Sensor(
      port=constants.SENSOR_PORT,
      num_grpc_threads=4,
      supervisor_config=config,
  )
  return sensor_instance


def create_host(
    config: supervisor_core.SupervisorConfig,
) -> host.Host:
  """Creates an instance of the Host pybind wrapper."""
  host_instance = host.Host(
      project_id="test-project",
      port=constants.HOST_PORT,
      supervisor_config=config,
  )
  return host_instance
