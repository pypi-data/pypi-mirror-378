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

import enum

import supervisor_core


@enum.unique
class DeviceState(enum.Enum):
  """The state of a physical device.

  Worker and Host objects can have six possible states. RUNNING denotes that the
  device is healthy and participating in training. SPARE denotes that the worker
  is healthy but not currently participating in training. FAILED denotes that
  the worker is currently unreachable. COMPLETE denotes that the worker has
  completed its training workload.
  """

  UNDEFINED = 0
  RUNNING = 1
  SPARE = 2
  FAILED = 3
  COMPLETE = 4


class WorkloadInfo:
  """Representation of workload information."""

  def __init__(
      self,
      workload_name: str,
      job_name: str,
      container_name: str,
      num_data_replicas: int,
      max_num_data_replicas: int,
      min_num_data_replicas: int,
      num_nodes_per_data_replica: int,
      container_termination_threshold_s: int,
      workload_downtime_threshold_s: int,
      max_in_job_restarts: int,
      max_workload_restarts: int,
      workload_scaling_enabled: bool,
  ):
    """WorkloadInfo constructor.

    Args:
        workload_name (str): The name of the workload. In GKE this is the name
          of the Jobset.
        job_name (str): The name of the job within the workload. In GKE this is
          the name of the ReplicatedJob within the Jobset.
        container_name (str): The name of the container running the workload.
        num_data_replicas (int): The number of data replicas the workload is
          initialized with.
        max_num_data_replicas (int): The maximum number of data replicas the
          workload can scale to.
        min_num_data_replicas (int): The minimum number of data replicas the
          workload can scale to.
        num_nodes_per_data_replica (int): The number of nodes per data replica.
        container_termination_threshold_s (int): The threshold in seconds for
          container termination.
        workload_downtime_threshold_s (int): The threshold in seconds for
          workload downtime.
        max_in_job_restarts (int): The maximum number of restarts for a job.
        max_workload_restarts (int): The maximum number of restarts for the
          workload.
        workload_scaling_enabled (bool): Whether workload scaling is enabled.
    """
    self._workload_name = workload_name
    self._job_name = job_name
    self._container_name = container_name
    self._num_data_replicas = num_data_replicas
    self._max_num_data_replicas = max_num_data_replicas
    self._min_num_data_replicas = min_num_data_replicas
    self._num_nodes_per_data_replica = num_nodes_per_data_replica
    self._container_termination_threshold_s = container_termination_threshold_s
    self._workload_downtime_threshold_s = workload_downtime_threshold_s
    self._max_in_job_restarts = max_in_job_restarts
    self._max_workload_restarts = max_workload_restarts
    self._workload_scaling_enabled = workload_scaling_enabled

    self._hosts = []

  def __repr__(self):
    return f"{self._workload_name}"

  def __eq__(self, other: "WorkloadInfo") -> bool:
    if not isinstance(other, WorkloadInfo):
      return False
    return (
        self.workload_name == other.workload_name
        and self.job_name == other.job_name
        and self.container_name == other.container_name
        and self.num_data_replicas == other.num_data_replicas
        and self.max_num_data_replicas == other.max_num_data_replicas
        and self.min_num_data_replicas == other.min_num_data_replicas
        and self.num_nodes_per_data_replica == other.num_nodes_per_data_replica
        and self.container_termination_threshold_s
        == other.container_termination_threshold_s
        and self.workload_downtime_threshold_s
        == other.workload_downtime_threshold_s
        and self.max_in_job_restarts == other.max_in_job_restarts
        and self.max_workload_restarts == other.max_workload_restarts
        and self.workload_scaling_enabled == other.workload_scaling_enabled
    )

  @property
  def workload_name(self) -> str:
    return self._workload_name

  @workload_name.setter
  def workload_name(self, workload_name: str):
    self._workload_name = workload_name

  @property
  def job_name(self) -> str:
    return self._job_name

  @job_name.setter
  def job_name(self, job_name: str):
    self._job_name = job_name

  @property
  def container_name(self) -> str:
    return self._container_name

  @container_name.setter
  def container_name(self, container_name: str):
    self._container_name = container_name

  @property
  def num_data_replicas(self) -> int:
    return self._num_data_replicas

  @num_data_replicas.setter
  def num_data_replicas(self, num_data_replicas: int):
    self._num_data_replicas = num_data_replicas

  @property
  def max_num_data_replicas(self) -> int:
    return self._max_num_data_replicas

  @max_num_data_replicas.setter
  def max_num_data_replicas(self, max_num_data_replicas: int):
    self._max_num_data_replicas = max_num_data_replicas

  @property
  def min_num_data_replicas(self) -> int:
    return self._min_num_data_replicas

  @min_num_data_replicas.setter
  def min_num_data_replicas(self, min_num_data_replicas: int):
    self._min_num_data_replicas = min_num_data_replicas

  @property
  def num_nodes_per_data_replica(self) -> int:
    return self._num_nodes_per_data_replica

  @num_nodes_per_data_replica.setter
  def num_nodes_per_data_replica(self, num_nodes_per_data_replica: int):
    self._num_nodes_per_data_replica = num_nodes_per_data_replica

  @property
  def container_termination_threshold_s(self) -> int:
    return self._container_termination_threshold_s

  @container_termination_threshold_s.setter
  def container_termination_threshold_s(
      self, container_termination_threshold_s: int
  ):
    self._container_termination_threshold_s = container_termination_threshold_s

  @property
  def workload_downtime_threshold_s(self) -> int:
    return self._workload_downtime_threshold_s

  @workload_downtime_threshold_s.setter
  def workload_downtime_threshold_s(self, workload_downtime_threshold_s: int):
    self._workload_downtime_threshold_s = workload_downtime_threshold_s

  @property
  def max_in_job_restarts(self) -> int:
    return self._max_in_job_restarts

  @max_in_job_restarts.setter
  def max_in_job_restarts(self, max_in_job_restarts: int):
    self._max_in_job_restarts = max_in_job_restarts

  @property
  def max_workload_restarts(self) -> int:
    return self._max_workload_restarts

  @max_workload_restarts.setter
  def max_workload_restarts(self, max_workload_restarts: int):
    self._max_workload_restarts = max_workload_restarts

  @property
  def workload_scaling_enabled(self) -> bool:
    return self._workload_scaling_enabled

  @workload_scaling_enabled.setter
  def workload_scaling_enabled(self, workload_scaling_enabled: bool):
    self._workload_scaling_enabled = workload_scaling_enabled

  def export_info(self) -> supervisor_core.WorkloadInfo:
    """Exports the workload information to a supervisor_core.WorkloadInfo object."""
    w_info = supervisor_core.WorkloadInfo()
    w_info.workload_name = self.workload_name
    w_info.job_name = self.job_name
    w_info.container_name = self.container_name
    w_info.num_data_replicas = self.num_data_replicas
    w_info.max_num_data_replicas = self.max_num_data_replicas
    w_info.min_num_data_replicas = self.min_num_data_replicas
    w_info.num_nodes_per_data_replica = self.num_nodes_per_data_replica
    w_info.container_termination_threshold_s = (
        self.container_termination_threshold_s
    )
    w_info.workload_downtime_threshold_s = self.workload_downtime_threshold_s
    w_info.max_in_job_restarts = self.max_in_job_restarts
    w_info.max_workload_restarts = self.max_workload_restarts
    w_info.workload_scaling_enabled = self.workload_scaling_enabled
    return w_info

  def update_info(self, workload_info_proto: supervisor_core.WorkloadInfo):
    """Updates the workload information from a supervisor_core.WorkloadInfo object."""
    self.workload_name = workload_info_proto.workload_name
    self.job_name = workload_info_proto.job_name
    self.container_name = workload_info_proto.container_name
    self.num_data_replicas = workload_info_proto.num_data_replicas
    self.max_num_data_replicas = workload_info_proto.max_num_data_replicas
    self.min_num_data_replicas = workload_info_proto.min_num_data_replicas
    self.num_nodes_per_data_replica = (
        workload_info_proto.num_nodes_per_data_replica
    )
    self.container_termination_threshold_s = (
        workload_info_proto.container_termination_threshold_s
    )
    self.workload_downtime_threshold_s = (
        workload_info_proto.workload_downtime_threshold_s
    )
    self.max_in_job_restarts = workload_info_proto.max_in_job_restarts
    self.max_workload_restarts = workload_info_proto.max_workload_restarts
    self.workload_scaling_enabled = workload_info_proto.workload_scaling_enabled


class HostInfo:
  """Representation of physical and virtual identifiers for a host machine."""

  def __init__(
      self,
      host_address: str,
      host_id: str,
      host_serial_number: str,
      host_name: str,
      subblock_id: str,
      superblock_id: str,
      zone: str,
      state: DeviceState = DeviceState.SPARE,
  ):
    """HostInfo constructor.

    Args:
        host_address (str): The network address of the host.
        host_id (str): The serial number of the host machine.
        host_serial_number (str): The host's serial number.
        host_name (str): Name of host's corresponding python process.
        subblock_id (str): The host's supblock. Defaults to None.
        superblock_id (str): The host's superblock. Defaults to None.
        zone (str): The host's zone. Defaults to None.
        state (DeviceState, optional): The state of the host. Defaults to
          DeviceState.SPARE.
    """
    # Physical Identifiers
    self._host_address = host_address
    self._host_id = host_id
    self._host_serial_number = host_serial_number
    self._subblock_id = subblock_id
    self._superblock_id = superblock_id
    self._zone = zone
    self._state = state

    # Virtual Identifiers
    self._host_name = host_name

    self._workers = []
    self._workload = None

  def __repr__(self):
    return f"{self._host_id}"

  def __eq__(self, other: "HostInfo") -> bool:
    if not isinstance(other, HostInfo):
      return False
    return (
        self.host_address == other.host_address
        and self.host_id == other.host_id
        and self.host_serial_number == other.host_serial_number
        and self.host_name == other.host_name
        and self.subblock_id == other.subblock_id
        and self.superblock_id == other.superblock_id
        and self.zone == other.zone
        and self.state == other.state
        and len(self.workers) == len(other.workers)
        and all([
            worker == other_worker
            for worker, other_worker in zip(
                self.workers, other.workers, strict=True
            )
        ])
    )

  @property
  def host_address(self) -> str:
    return self._host_address

  @property
  def host_id(self) -> str:
    return self._host_id

  @property
  def host_serial_number(self) -> str:
    return self._host_serial_number

  @property
  def subblock_id(self) -> str:
    return self._subblock_id

  @property
  def superblock_id(self) -> str:
    return self._superblock_id

  @property
  def zone(self) -> str:
    return self._zone

  @property
  def state(self) -> DeviceState:
    return self._state

  @state.setter
  def state(self, state: DeviceState):
    self._state = state

  @property
  def workers(self) -> list["WorkerInfo"]:
    return self._workers

  @workers.setter
  def workers(self, workers: list["WorkerInfo"]):
    self._workers = workers

  @property
  def workload(self) -> supervisor_core.WorkloadInfo | None:
    return self._workload

  @workload.setter
  def workload(self, workload: supervisor_core.WorkloadInfo):
    self._workload = workload

  @property
  def host_name(self) -> str:
    return self._host_name

  def export_info(self) -> supervisor_core.HostInfo:
    """Exports the host information to a supervisor_core.HostInfo object.

    Returns:
        supervisor_core.HostInfo: A supervisor_core.HostInfo object.
    """
    h_info = supervisor_core.HostInfo()
    h_info.host_address = self.host_address
    h_info.host_id = self.host_id
    h_info.host_name = self.host_name
    h_info.subblock_id = self.subblock_id
    h_info.superblock_id = self.superblock_id
    h_info.host_serial_number = self.host_serial_number
    h_info.zone = self.zone
    h_info.state = supervisor_core.DeviceState(self.state.value)
    h_info.workers = [worker.export_info() for worker in self.workers]

    if self.workload is not None:
      h_info.workload = self.workload.export_info()
    else:
      h_info.workload = supervisor_core.WorkloadInfo()

    return h_info

  def update_info(self, host_info_proto: supervisor_core.HostInfo):
    """Updates the host information from a supervisor_core.HostInfo object.

    Args:
        host_info_proto (supervisor_core.HostInfo): The supervisor_core.HostInfo
          object to update from.
    """
    self.state = DeviceState(host_info_proto.state.value)
    self.workload = workload_info_from_proto(host_info_proto.workload)

    self.workers.clear()
    for worker_info_proto in host_info_proto.workers:
      self.workers.append(worker_info_from_proto(worker_info_proto))

  def get_num_workers(self) -> int:
    """Gets the number of running workers associated with this host.

    Returns:
        int: The number of running workers.
    """
    return len([
        worker
        for worker in self._workers
        if worker.state == DeviceState.RUNNING
    ])


class WorkerInfo:
  """Representation of physical and virtual identifiers for a GPU Worker."""

  def __init__(
      self,
      worker_address: str,
      worker_id: str,
      worker_name: str | None = None,
      local_rank: int | None = None,
      global_rank: int | None = None,
      state: DeviceState = DeviceState.RUNNING,
  ):
    """WorkerInfo constructor.

    Args:
        worker_address (str): The network address of the worker.
        worker_id (str): The serial number of the GPU associated with the
          worker.
        worker_name (str | None): Name of worker's corresponding python process.
          Defaults to None.
        local_rank (int | None): The worker's rank respective to the host.
        global_rank (int | None): The worker's rank respective to the entire
          workload.
        state (DeviceState): The state of the worker. Defaults to
          DeviceState.AVAILABLE.
    """
    # Physical Identifiers
    self._worker_address = worker_address
    self._host = None
    self._worker_id = worker_id
    self._state = state

    # Virtual Identifiers
    self._local_rank = local_rank
    self._global_rank = global_rank
    self._worker_name = worker_name

  def __repr__(self):
    return f"{self._worker_id}"

  def __eq__(self, other: "WorkerInfo") -> bool:
    if not isinstance(other, WorkerInfo):
      return False
    return (
        self.worker_address == other.worker_address
        and self.worker_id == other.worker_id
        and self.worker_name == other.worker_name
        and self.local_rank == other.local_rank
        and self.global_rank == other.global_rank
        and self.state == other.state
    )

  @property
  def host(self) -> HostInfo | None:
    return self._host

  @host.setter
  def host(self, host: HostInfo):
    self._host = host

  @property
  def worker_address(self) -> str:
    return self._worker_address

  @worker_address.setter
  def worker_address(self, address: str):
    self._worker_address = address

  @property
  def worker_id(self) -> str:
    return self._worker_id

  @property
  def state(self) -> DeviceState:
    return self._state

  @state.setter
  def state(self, state: DeviceState):
    self._state = state

  @property
  def local_rank(self) -> int | None:
    return self._local_rank

  @local_rank.setter
  def local_rank(self, rank: int):
    self._local_rank = rank

  @property
  def global_rank(self) -> int | None:
    return self._global_rank

  @global_rank.setter
  def global_rank(self, rank: int):
    self._global_rank = rank

  @property
  def worker_name(self) -> str:
    if self._worker_name is None:
      self._worker_name = f"worker_{self.worker_id}"
    return self._worker_name

  def export_info(self) -> supervisor_core.WorkerInfo:
    """Exports the worker information to a supervisor_core.WorkerInfo object.

    Returns:
        supervisor_core.WorkerInfo: A supervisor_core.WorkerInfo object.
    """
    w_info = supervisor_core.WorkerInfo()
    w_info.worker_address = self.worker_address
    w_info.worker_id = self.worker_id
    w_info.worker_name = self.worker_name
    w_info.local_rank = -1 if self.local_rank is None else self.local_rank
    w_info.global_rank = -1 if self.global_rank is None else self.global_rank
    w_info.state = supervisor_core.DeviceState(self.state.value)
    return w_info

  def update_info(self, worker_info_proto: supervisor_core.WorkerInfo):
    """Updates the worker information from a supervisor_core.WorkerInfo object.

    Args:
        worker_info_proto (supervisor_core.WorkerInfo): The
          supervisor_core.WorkerInfo object to update from.
    """
    self.local_rank = worker_info_proto.local_rank
    self.global_rank = worker_info_proto.global_rank
    self.state = DeviceState(worker_info_proto.state.value)


def host_info_from_proto(host_info_proto: supervisor_core.HostInfo) -> HostInfo:
  """Converts a supervisor_core.HostInfo object to a device_info.HostInfo object.

  Args:
      host_info_proto (supervisor_core.HostInfo): The supervisor_core.HostInfo
        object to convert.

  Returns:
      HostInfo: A device_info.HostInfo object.
  """
  host_info = HostInfo(
      host_address=host_info_proto.host_address,
      host_id=host_info_proto.host_id,
      host_serial_number=host_info_proto.host_serial_number,
      host_name=host_info_proto.host_name,
      subblock_id=host_info_proto.subblock_id,
      superblock_id=host_info_proto.superblock_id,
      zone=host_info_proto.zone,
      state=DeviceState(host_info_proto.state),
  )
  workers = [
      worker_info_from_proto(worker_info_proto)
      for worker_info_proto in host_info_proto.workers
  ]
  for worker in workers:
    worker.host = host_info
  host_info.workers = workers
  return host_info


def worker_info_from_proto(
    worker_info_proto: supervisor_core.WorkerInfo,
) -> WorkerInfo:
  """Converts a supervisor_core.WorkerInfo object to a device_info.WorkerInfo object.

  Args:
      worker_info_proto (supervisor_core.WorkerInfo): The
        supervisor_core.WorkerInfo object to convert.

  Returns:
      WorkerInfo: A device_info.WorkerInfo object.
  """
  worker_info = WorkerInfo(
      worker_address=worker_info_proto.worker_address,
      worker_id=worker_info_proto.worker_id,
      local_rank=worker_info_proto.local_rank,
      global_rank=worker_info_proto.global_rank,
      worker_name=worker_info_proto.worker_name,
      state=DeviceState(worker_info_proto.state),
  )
  return worker_info


def workload_info_from_proto(
    workload_info_proto: supervisor_core.WorkloadInfo,
) -> WorkloadInfo:
  """Converts a supervisor_core.WorkloadInfo object to a device_info.WorkloadInfo object.

  Args:
      workload_info_proto (supervisor_core.WorkloadInfo): The
        supervisor_core.WorkloadInfo object to convert.

  Returns:
      WorkloadInfo: A device_info.WorkloadInfo object.
  """
  workload_info = WorkloadInfo(
      workload_name=workload_info_proto.workload_name,
      job_name=workload_info_proto.job_name,
      container_name=workload_info_proto.container_name,
      num_data_replicas=workload_info_proto.num_data_replicas,
      max_num_data_replicas=workload_info_proto.max_num_data_replicas,
      min_num_data_replicas=workload_info_proto.min_num_data_replicas,
      num_nodes_per_data_replica=workload_info_proto.num_nodes_per_data_replica,
      container_termination_threshold_s=workload_info_proto.container_termination_threshold_s,
      workload_downtime_threshold_s=workload_info_proto.workload_downtime_threshold_s,
      max_in_job_restarts=workload_info_proto.max_in_job_restarts,
      max_workload_restarts=workload_info_proto.max_workload_restarts,
      workload_scaling_enabled=workload_info_proto.workload_scaling_enabled,
  )
  return workload_info
