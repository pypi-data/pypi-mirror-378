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
import sys

import pytest
from supervisor.core.python import device_info
import supervisor_core


class TestDeviceInfo:
  """Tests the functionality of WorkerInfo and HostInfo classes.

  This includes testing initialization, serialization to protobuf, updating
  from protobuf, and conversion from protobuf to Python objects.
  """

  @pytest.mark.parametrize(
      (
          "worker_info",
          "expected_worker_proto",
      ),
      (
          (
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              supervisor_core.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  supervisor_core.DeviceState.RUNNING,
              ),
          ),
          (
              device_info.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  0,
                  device_info.DeviceState.SPARE,
              ),
              supervisor_core.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  0,
                  supervisor_core.DeviceState.SPARE,
              ),
          ),
      ),
  )
  def test_serialize_worker(
      self,
      worker_info: device_info.WorkerInfo,
      expected_worker_proto: supervisor_core.WorkerInfo,
  ):
    worker_proto = worker_info.export_info()
    assert worker_proto.worker_address == expected_worker_proto.worker_address
    assert worker_proto.worker_id == expected_worker_proto.worker_id
    assert worker_proto.local_rank == expected_worker_proto.local_rank
    assert worker_proto.global_rank == expected_worker_proto.global_rank
    assert worker_proto.state == expected_worker_proto.state
    assert worker_proto.worker_name == expected_worker_proto.worker_name

  @pytest.mark.parametrize(
      (
          "worker_info",
          "expected_repr",
      ),
      (
          (
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              "worker_id_0",
          ),
          (
              device_info.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  0,
                  device_info.DeviceState.SPARE,
              ),
              "worker_id_1",
          ),
      ),
  )
  def test_worker_info_repr(
      self, worker_info: device_info.WorkerInfo, expected_repr: str
  ):
    assert str(worker_info) == expected_repr

  @pytest.mark.parametrize(
      (
          "worker_info_a",
          "worker_info_b",
          "expected_eq",
      ),
      (
          (
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              True,
          ),
          (
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              device_info.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  1,
                  device_info.DeviceState.SPARE,
              ),
              False,
          ),
      ),
  )
  def test_worker_info_eq(
      self,
      worker_info_a: device_info.WorkerInfo,
      worker_info_b: device_info.WorkerInfo,
      expected_eq: bool,
  ):
    assert (worker_info_a == worker_info_b) == expected_eq

  @pytest.mark.parametrize(
      (
          "worker_info",
          "worker_info_proto",
      ),
      (
          (
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              supervisor_core.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  1,
                  supervisor_core.DeviceState.SPARE,
              ),
          ),
          (
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
              supervisor_core.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  supervisor_core.DeviceState.RUNNING,
              ),
          ),
      ),
  )
  def test_update_worker(
      self,
      worker_info: device_info.WorkerInfo,
      worker_info_proto: supervisor_core.WorkerInfo,
  ):
    worker_info_previous = copy.copy(worker_info)
    worker_info.update_info(worker_info_proto)

    assert worker_info.worker_address == worker_info_previous.worker_address
    assert worker_info.worker_id == worker_info_previous.worker_id
    assert worker_info.worker_name == worker_info_previous.worker_name

    assert worker_info.local_rank == worker_info_proto.local_rank
    assert worker_info.global_rank == worker_info_proto.global_rank
    assert worker_info.state == device_info.DeviceState(
        worker_info_proto.state.value
    )

  @pytest.mark.parametrize(
      (
          "worker_proto",
          "expected_worker_info",
      ),
      (
          (
              supervisor_core.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  0,
                  supervisor_core.DeviceState.FAILED,
              ),
              device_info.WorkerInfo(
                  "worker_address_1",
                  "worker_id_1",
                  "worker_name_1",
                  1,
                  0,
                  device_info.DeviceState.FAILED,
              ),
          ),
          (
              supervisor_core.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  supervisor_core.DeviceState.RUNNING,
              ),
              device_info.WorkerInfo(
                  "worker_address_0",
                  "worker_id_0",
                  "worker_name_0",
                  0,
                  0,
                  device_info.DeviceState.RUNNING,
              ),
          ),
      ),
  )
  def test_convert_worker_info(
      self,
      worker_proto: supervisor_core.WorkerInfo,
      expected_worker_info: device_info.WorkerInfo,
  ):
    converted_worker_info = device_info.worker_info_from_proto(worker_proto)
    assert converted_worker_info == expected_worker_info

  @pytest.mark.parametrize(
      (
          "host_info",
          "expected_repr",
      ),
      (
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              "host_id_0",
          ),
          (
              device_info.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  device_info.DeviceState.SPARE,
              ),
              "host_id_1",
          ),
      ),
  )
  def test_host_info_repr(
      self, host_info: device_info.HostInfo, expected_repr: str
  ):
    assert str(host_info) == expected_repr

  @pytest.mark.parametrize(
      (
          "host_info_a",
          "host_info_b",
          "expected_eq",
      ),
      (
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              True,
          ),
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              device_info.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  device_info.DeviceState.SPARE,
              ),
              False,
          ),
      ),
  )
  def test_host_info_eq(
      self,
      host_info_a: device_info.HostInfo,
      host_info_b: device_info.HostInfo,
      expected_eq: bool,
  ):
    assert (host_info_a == host_info_b) == expected_eq

  @pytest.mark.parametrize(
      (
          "host_info",
          "expected_host_proto",
      ),
      (
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              supervisor_core.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  supervisor_core.DeviceState.RUNNING,
              ),
          ),
          (
              device_info.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  device_info.DeviceState.SPARE,
              ),
              supervisor_core.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  supervisor_core.DeviceState.SPARE,
              ),
          ),
      ),
  )
  def test_serialize_host(
      self,
      host_info: device_info.HostInfo,
      expected_host_proto: supervisor_core.HostInfo,
  ):
    host_proto = host_info.export_info()

    assert host_proto.host_address == expected_host_proto.host_address
    assert host_proto.host_id == expected_host_proto.host_id
    assert (
        host_proto.host_serial_number == expected_host_proto.host_serial_number
    )
    assert host_proto.subblock_id == expected_host_proto.subblock_id
    assert host_proto.superblock_id == expected_host_proto.superblock_id
    assert host_proto.zone == expected_host_proto.zone
    assert host_proto.host_name == expected_host_proto.host_name
    assert host_proto.state == expected_host_proto.state

  @pytest.mark.parametrize(
      (
          "host_info",
          "expected_host_proto",
      ),
      (
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              supervisor_core.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  supervisor_core.DeviceState.SPARE,
              ),
          ),
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              supervisor_core.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  supervisor_core.DeviceState.RUNNING,
              ),
          ),
      ),
  )
  def test_update_host(
      self,
      host_info: device_info.HostInfo,
      expected_host_proto: supervisor_core.HostInfo,
  ):
    host_info_previous = copy.copy(host_info)
    host_info.update_info(expected_host_proto)

    assert host_info.host_address == host_info_previous.host_address
    assert host_info.host_id == host_info_previous.host_id
    assert host_info.host_serial_number == host_info_previous.host_serial_number
    assert host_info.subblock_id == host_info_previous.subblock_id
    assert host_info.superblock_id == host_info_previous.superblock_id
    assert host_info.zone == host_info_previous.zone
    assert host_info.host_name == host_info_previous.host_name

    assert host_info.state == device_info.DeviceState(
        expected_host_proto.state.value
    )

  @pytest.mark.parametrize(
      (
          "host_proto",
          "expected_host_info",
      ),
      (
          (
              supervisor_core.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  supervisor_core.DeviceState.RUNNING,
              ),
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
          ),
          (
              supervisor_core.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  supervisor_core.DeviceState.SPARE,
              ),
              device_info.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  device_info.DeviceState.SPARE,
              ),
          ),
      ),
  )
  def test_convert_host_info(
      self,
      host_proto: device_info.HostInfo,
      expected_host_info: device_info.HostInfo,
  ):
    converted_host_info = device_info.host_info_from_proto(host_proto)
    assert expected_host_info == converted_host_info

  @pytest.mark.parametrize(
      (
          "host_info",
          "expected_num_workers",
      ),
      (
          (
              device_info.HostInfo(
                  "host_address_0",
                  "host_id_0",
                  "host_serial_number_0",
                  "subblock_id_0",
                  "superblock_id_0",
                  "zone_0",
                  "host_name_0",
                  device_info.DeviceState.RUNNING,
              ),
              0,
          ),
          (
              device_info.HostInfo(
                  "host_address_1",
                  "host_id_1",
                  "host_serial_number_1",
                  "subblock_id_1",
                  "superblock_id_1",
                  "zone_1",
                  "host_name_1",
                  device_info.DeviceState.RUNNING,
              ),
              1,
          ),
      ),
  )
  def test_get_num_workers(
      self, host_info: device_info.HostInfo, expected_num_workers: int
  ):
    worker1 = device_info.WorkerInfo(
        "worker_address_0",
        "worker_id_0",
        "worker_name_0",
        0,
        0,
        device_info.DeviceState.RUNNING,
    )
    worker2 = device_info.WorkerInfo(
        "worker_address_1",
        "worker_id_1",
        "worker_name_1",
        1,
        1,
        device_info.DeviceState.SPARE,
    )
    if expected_num_workers > 0:
      host_info.workers = [worker1, worker2]

    assert host_info.get_num_workers() == expected_num_workers

  @pytest.mark.parametrize(
      (
          "workload_info",
          "expected_repr",
      ),
      (
          (
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              "workload_name_0",
          ),
      ),
  )
  def test_workload_info_repr(
      self, workload_info: device_info.WorkloadInfo, expected_repr: str
  ):
    assert str(workload_info) == expected_repr

  @pytest.mark.parametrize(
      (
          "workload_info_a",
          "workload_info_b",
          "expected_eq",
      ),
      (
          (
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              True,
          ),
          (
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              device_info.WorkloadInfo(
                  workload_name="workload_name_1",
                  job_name="job_name_1",
                  container_name="container_name_1",
                  num_data_replicas=2,
                  max_num_data_replicas=4,
                  min_num_data_replicas=2,
                  num_nodes_per_data_replica=2,
                  container_termination_threshold_s=110,
                  workload_downtime_threshold_s=210,
                  max_in_job_restarts=5,
                  max_workload_restarts=6,
                  workload_scaling_enabled=False,
              ),
              False,
          ),
      ),
  )
  def test_workload_info_eq(
      self,
      workload_info_a: device_info.WorkloadInfo,
      workload_info_b: device_info.WorkloadInfo,
      expected_eq: bool,
  ):
    assert (workload_info_a == workload_info_b) == expected_eq

  @pytest.mark.parametrize(
      ("workload_info", "expected_workload_proto"),
      (
          (
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              supervisor_core.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
          ),
      ),
  )
  def test_serialize_workload(
      self,
      workload_info: device_info.WorkloadInfo,
      expected_workload_proto: supervisor_core.WorkloadInfo,
  ):
    workload_proto = workload_info.export_info()
    assert workload_proto.workload_name == expected_workload_proto.workload_name
    assert workload_proto.job_name == expected_workload_proto.job_name
    assert (
        workload_proto.container_name == expected_workload_proto.container_name
    )
    assert (
        workload_proto.num_data_replicas
        == expected_workload_proto.num_data_replicas
    )
    assert (
        workload_proto.max_num_data_replicas
        == expected_workload_proto.max_num_data_replicas
    )
    assert (
        workload_proto.min_num_data_replicas
        == expected_workload_proto.min_num_data_replicas
    )
    assert (
        workload_proto.num_nodes_per_data_replica
        == expected_workload_proto.num_nodes_per_data_replica
    )
    assert (
        workload_proto.container_termination_threshold_s
        == expected_workload_proto.container_termination_threshold_s
    )
    assert (
        workload_proto.workload_downtime_threshold_s
        == expected_workload_proto.workload_downtime_threshold_s
    )
    assert (
        workload_proto.max_in_job_restarts
        == expected_workload_proto.max_in_job_restarts
    )
    assert (
        workload_proto.max_workload_restarts
        == expected_workload_proto.max_workload_restarts
    )
    assert (
        workload_proto.workload_scaling_enabled
        == expected_workload_proto.workload_scaling_enabled
    )

  @pytest.mark.parametrize(
      ("workload_info", "workload_info_proto"),
      (
          (
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              supervisor_core.WorkloadInfo(
                  workload_name="workload_name_1",
                  job_name="job_name_1",
                  container_name="container_name_1",
                  num_data_replicas=2,
                  max_num_data_replicas=4,
                  min_num_data_replicas=2,
                  num_nodes_per_data_replica=2,
                  container_termination_threshold_s=110,
                  workload_downtime_threshold_s=210,
                  max_in_job_restarts=5,
                  max_workload_restarts=6,
                  workload_scaling_enabled=False,
              ),
          ),
      ),
  )
  def test_update_workload(
      self,
      workload_info: device_info.WorkloadInfo,
      workload_info_proto: supervisor_core.WorkloadInfo,
  ):
    workload_info.update_info(workload_info_proto)
    expected_workload_info = device_info.workload_info_from_proto(
        workload_info_proto
    )
    assert workload_info == expected_workload_info

  @pytest.mark.parametrize(
      ("workload_proto", "expected_workload_info"),
      (
          (
              supervisor_core.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
              device_info.WorkloadInfo(
                  workload_name="workload_name_0",
                  job_name="job_name_0",
                  container_name="container_name_0",
                  num_data_replicas=1,
                  max_num_data_replicas=2,
                  min_num_data_replicas=1,
                  num_nodes_per_data_replica=1,
                  container_termination_threshold_s=100,
                  workload_downtime_threshold_s=200,
                  max_in_job_restarts=3,
                  max_workload_restarts=4,
                  workload_scaling_enabled=True,
              ),
          ),
      ),
  )
  def test_convert_workload_info(
      self,
      workload_proto: supervisor_core.WorkloadInfo,
      expected_workload_info: device_info.WorkloadInfo,
  ):
    converted_workload_info = device_info.workload_info_from_proto(
        workload_proto
    )
    assert converted_workload_info == expected_workload_info


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
