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

import socket

from supervisor.client.python import utils
from supervisor.core.python import device_info
from supervisor.core.python import utils as core_utils
import supervisor_core


class GoogleCloudResiliencyClient:
  """Abstraction instantiated by user workload to manage communication with Host.

  Stores all metadata related to a worker process, including physical worker
  attributes and worker rank. Additionally, this abstraction houses the
  communication infrastructure between the worker and the Host process.
  """

  def __init__(
      self,
      port: int,
      host_port: str,
      local_rank: int,
      global_rank: int,
      workload_name: str,
      job_name: str = "",
      container_name: str = "",
      num_data_replicas: int = 0,
      max_num_data_replicas: int = 0,
      min_num_data_replicas: int = 0,
      num_nodes_per_data_replica: int = 0,
      container_termination_threshold_s: int = 60,
      workload_downtime_threshold_s: int = 180,
      max_in_job_restarts: int = 0,
      max_workload_restarts: int = 1,
      workload_scaling_enabled: bool = False,
  ):
    """Constructs a GoogleResiliencyClient object.

    Args:
        port: The port on which to run workload communication.
        host_port: The port running the host process.
        local_rank: The local rank of the worker processes.
        global_rank: The global rank of the worker processes.
        workload_name: The name of the workload. In GKE this is the name of the
          Jobset.
        job_name: The name of the job within the workload. In GKE this is the
          name of the ReplicatedJob within the Jobset.
        container_name: The name of the container running the workload.
        num_data_replicas: The number of data replicas the workload is
          initialized with.
        max_num_data_replicas: The maximum number of data replicas the workload
          can scale up to.
        min_num_data_replicas: The minimum number of data replicas the workload
          can scale down to.
        num_nodes_per_data_replica: The number of nodes per data replica.
        container_termination_threshold_s: The time in seconds after which the
          container will be terminated if it does not exit gracefully. In GKE
          this limits how long Pods can be in the "Terminating" phase.
        workload_downtime_threshold_s: The time in seconds after which the
          workload will be recreated if it does not exit gracefully. In GKE this
          limits how long Jobset Pods can be in any phase other than "Running".
        max_in_job_restarts: The maximum number of in-job restarts before a
          worload restart is triggered.
        max_workload_restarts: The maximum number of workload restarts before a
          hot-swap or scaling operation is triggered.
        workload_scaling_enabled: Whether workload scaling is enabled.
    """
    host_address = f"localhost:" + str(host_port)
    pci_bus_id = utils.get_pci_bus_id(local_rank)

    self.logger = core_utils.setup_logger()

    # Collect metadata related to worker
    self._worker_info = device_info.WorkerInfo(
        worker_address="localhost:" + str(port),
        worker_name=f"{socket.gethostname()}-{pci_bus_id}",
        worker_id=pci_bus_id,
        local_rank=local_rank,
        global_rank=global_rank,
    )

    # Collect metadata related to workload
    self._workload_info = device_info.WorkloadInfo(
        workload_name=workload_name,
        job_name=job_name,
        container_name=container_name,
        num_data_replicas=num_data_replicas,
        max_num_data_replicas=max_num_data_replicas,
        min_num_data_replicas=min_num_data_replicas,
        num_nodes_per_data_replica=num_nodes_per_data_replica,
        container_termination_threshold_s=container_termination_threshold_s,
        workload_downtime_threshold_s=workload_downtime_threshold_s,
        max_in_job_restarts=max_in_job_restarts,
        max_workload_restarts=max_workload_restarts,
        workload_scaling_enabled=workload_scaling_enabled,
    )

    # Initialize Worker gRPC server
    self._worker = supervisor_core.Worker(
        worker_info=self.export_info(),
        host_address=host_address,
    )
    self._worker.register_workload(self.export_workload_info())
    self.logger.info(
        "Initializing GoogleCloudResiliencyClient for worker"
        f" {self.worker_name} running workload {self.workload_name}"
    )
    self.logger.info(
        f"Workload {self.workload_name} remediation config:"
        f" {self.workload_scaling_enabled=}, {self.max_workload_restarts=},"
        f" {self.max_in_job_restarts=}."
    )

  @property
  def worker_info(self) -> device_info.WorkerInfo:
    """The information of the worker process."""
    return self._worker_info

  @property
  def worker_name(self) -> str:
    """The name of the worker process."""
    return self.worker_info.worker_name

  @property
  def worker_id(self) -> str:
    """The PCI Bus ID of the GPU associated with the worker."""
    return self.worker_info.worker_id

  @property
  def local_rank(self) -> int:
    """The local rank of the worker process."""
    return self.worker_info.local_rank

  @local_rank.setter
  def local_rank(self, value: int):
    """Set the local rank of the worker process.

    Args:
        value: The new local rank of the worker.
    """
    self.worker_info.local_rank = value

  @property
  def global_rank(self) -> int:
    """The global rank of the worker process."""
    return self.worker_info.global_rank

  @global_rank.setter
  def global_rank(self, value: int):
    """Set the global rank of the worker process.

    Args:
        value: The new global rank of the worker.
    """
    self.worker_info.global_rank = value

  @property
  def state(self) -> device_info.DeviceState:
    """The current state of the worker."""
    return self.worker_info.state

  @property
  def workload_name(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.workload_name

  @property
  def job_name(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.job_name

  @property
  def container_name(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.container_name

  @property
  def num_data_replicas(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.num_data_replicas

  @property
  def max_num_data_replicas(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.max_num_data_replicas

  @property
  def min_num_data_replicas(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.min_num_data_replicas

  @property
  def num_nodes_per_data_replica(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.num_nodes_per_data_replica

  @property
  def container_termination_threshold_s(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.container_termination_threshold_s

  @property
  def workload_downtime_threshold_s(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.workload_downtime_threshold_s

  @property
  def max_in_job_restarts(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.max_in_job_restarts

  @property
  def max_workload_restarts(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.max_workload_restarts

  @property
  def workload_scaling_enabled(self) -> device_info.WorkloadInfo:
    """The information of the workload."""
    return self._workload_info.workload_scaling_enabled

  @state.setter
  def state(self, value: device_info.DeviceState):
    """Set the current state of the worker.

    Args:
        value: The new state of the worker.

    Raises:
        ValueError: If the value is not a valid state.
    """

    if value not in (
        device_info.DeviceState.RUNNING,
        device_info.DeviceState.FAILED,
        device_info.DeviceState.COMPLETE,
    ):
      raise ValueError(f"Invalid state: {value}")

    self.worker_info.state = value

  def export_info(self) -> supervisor_core.WorkerInfo:
    """Export Worker object into supervisor_core WorkerInfo object."""
    return self.worker_info.export_info()

  def export_workload_info(self) -> supervisor_core.WorkloadInfo:
    """Export Workload object into supervisor_core WorkloadInfo object."""
    return self._workload_info.export_info()

  def update_info(self, worker_info: supervisor_core.WorkerInfo):
    """Update the metadata associated with the worker."""
    self.worker_info.update_info(worker_info)

  def update_workload_info(self, workload_info: supervisor_core.WorkloadInfo):
    """Update the metadata associated with the workload."""
    self._workload_info.update_info(workload_info)

  def send_heartbeat(self):
    """Communicate Worker state to the Host."""
    self._worker.send_heartbeat(self.export_info())

  def update_state(self, state: device_info.DeviceState):
    """Update the state of the worker and send a heartbeat."""
    self.state = state
    self.send_heartbeat()
