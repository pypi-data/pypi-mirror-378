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

import time

import supervisor.core.python.utils as core_utils
import supervisor_core


class Actuator:
  """Abstraction of actuator processes of the Supervisor.

  Stores all metadata related to the Actuator process and provides an interface
  to interact with the Actuator process. The Actuator process is responsible for
  communicating Controller commands to Hosts in the cluster.
  """

  def __init__(
      self,
      port: int,
      num_grpc_threads: int,
      supervisor_config: supervisor_core.SupervisorConfig | None = None,
  ):
    """Constructs the Actuator object.

    Args:
        port: The port on which to run the actuator communication.
        num_grpc_threads: The number of gRPC threads to initialize for
          communication.
        supervisor_config: The config object for Supervisor components.
    """
    self.logger = core_utils.setup_logger()

    if not supervisor_config:
      supervisor_config = supervisor_core.SupervisorConfig.from_environment()

    self._actuator = supervisor_core.Actuator(
        port=port, num_grpc_threads=num_grpc_threads, config=supervisor_config
    )

    self._actuator.start()
    while not self._actuator.is_ready():
      continue

    self._actuator_address = supervisor_config.actuator_address
    self.logger.info(
        f"Successfully started actuator process at address: {self.address}"
    )

  def __repr__(self) -> str:
    return f"{self.name}@{self.address}"

  @property
  def name(self) -> str:
    """Returns the name of the Actuator process."""
    return "actuator"

  @property
  def address(self) -> str:
    """Returns the address of the Actuator process."""
    return self._actuator_address

  @property
  def num_hosts(self) -> str:
    """Returns the total number of hosts currently tracked by the actuator."""
    return self._actuator.num_hosts()

  @property
  def num_running_hosts(self) -> str:
    """Returns the number of hosts participating in training currently tracked by the actuator."""
    return self._actuator.num_running_hosts()

  @property
  def num_spare_hosts(self) -> str:
    """Returns the number of spare hosts currently tracked by the actuator."""
    return self._actuator.num_spare_hosts()

  def shutdown(self):
    """Shuts doen the actuator process and child threads."""
    self._actuator.shutdown()

  def wait_for_completion(self):
    """Waits for all hosts registered to actuator to finish their workloads."""
    while not self._actuator.is_complete():
      time.sleep(10)
