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
from supervisor.client.python import utils
from supervisor.client.python import workload
from supervisor.core.python import device_info
import supervisor_core


class TestGoogleCloudResiliencyClient:
  """Unit tests for the GoogleCloudResiliencyClient class."""

  @pytest.fixture(autouse=True)
  def setup_method(self):
    self.mock_worker_cls = mock.patch.object(
        supervisor_core, "Worker", autospec=True
    ).start()
    self.mock_worker_instance = self.mock_worker_cls.return_value
    self.mock_get_pci_bus_id = mock.patch.object(
        utils, "get_pci_bus_id", autospec=True
    ).start()
    self.mock_get_pci_bus_id.return_value = "0000:01:00.0"
    self.port = 5001
    self.host_port = "5000"
    self.local_rank = 0
    self.global_rank = 2
    self.workload_name = "test_workload"
    self.job_name = "test_job"
    self.container_name = "test_container"
    self.num_data_replicas = 1
    self.max_num_data_replicas = 1
    self.min_num_data_replicas = 1
    self.num_nodes_per_data_replica = 1
    self.container_termination_threshold_s = 10
    self.workload_downtime_threshold_s = 10
    self.max_in_job_restarts = 0
    self.max_workload_restarts = 0
    self.workload_scaling_enabled = False

  @pytest.fixture(autouse=True)
  def teardown_method(self):
    yield
    mock.patch.stopall()

  def test_init_success(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    self.mock_get_pci_bus_id.assert_called_once_with(self.local_rank)
    self.mock_worker_cls.assert_called_once()
    assert client.worker_info.worker_address == f"localhost:{self.port}"
    assert client.worker_info.worker_name is not None
    assert client.worker_info.worker_id == "0000:01:00.0"
    assert client.local_rank == self.local_rank
    assert client.global_rank == self.global_rank
    assert client.workload_name == self.workload_name
    assert client.job_name == self.job_name
    assert client.container_name == self.container_name
    assert client.num_data_replicas == self.num_data_replicas
    assert client.max_num_data_replicas == self.max_num_data_replicas
    assert client.min_num_data_replicas == self.min_num_data_replicas
    assert client.num_nodes_per_data_replica == self.num_nodes_per_data_replica
    assert (
        client.container_termination_threshold_s
        == self.container_termination_threshold_s
    )
    assert (
        client.workload_downtime_threshold_s
        == self.workload_downtime_threshold_s
    )
    assert client.max_in_job_restarts == self.max_in_job_restarts
    assert client.max_workload_restarts == self.max_workload_restarts
    assert client.workload_scaling_enabled == self.workload_scaling_enabled

  def test_init_with_default_values(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
    )
    self.mock_get_pci_bus_id.assert_called_once_with(self.local_rank)
    self.mock_worker_cls.assert_called_once()
    assert client.worker_info.worker_address == f"localhost:{self.port}"
    assert client.worker_info.worker_name is not None
    assert client.worker_info.worker_id == "0000:01:00.0"
    assert client.local_rank == self.local_rank
    assert client.global_rank == self.global_rank
    assert client.workload_name == self.workload_name
    assert not client.job_name
    assert not client.container_name
    assert client.num_data_replicas == 0
    assert client.max_num_data_replicas == 0
    assert client.min_num_data_replicas == 0
    assert client.num_nodes_per_data_replica == 0
    assert client.container_termination_threshold_s == 60
    assert client.workload_downtime_threshold_s == 180
    assert client.max_in_job_restarts == 0
    assert client.max_workload_restarts == 1
    assert not client.workload_scaling_enabled

  def test_worker_info_property(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    assert isinstance(client.worker_info, device_info.WorkerInfo)
    assert client.worker_info.worker_address == f"localhost:{self.port}"
    assert client.worker_info.worker_name is not None
    assert client.worker_info.worker_id == "0000:01:00.0"
    assert client.worker_info.local_rank == self.local_rank
    assert client.worker_info.global_rank == self.global_rank

  def test_worker_name_property(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    assert client.worker_name is not None

  def test_worker_id_property(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    assert client.worker_id == "0000:01:00.0"

  def test_local_rank_property_and_setter(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    client.local_rank = 1
    assert client.local_rank == 1

  def test_global_rank_property_and_setter(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    client.global_rank = 3
    assert client.global_rank == 3

  def test_state_property_and_setter_valid(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    client.state = device_info.DeviceState.RUNNING
    assert client.state == device_info.DeviceState.RUNNING
    client.state = device_info.DeviceState.FAILED
    assert client.state == device_info.DeviceState.FAILED
    client.state = device_info.DeviceState.COMPLETE
    assert client.state == device_info.DeviceState.COMPLETE

  def test_state_property_and_setter_invalid(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    with pytest.raises(ValueError, match="Invalid state"):
      client.state = device_info.DeviceState.SPARE

  def test_export_info(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    exported_info = client.export_info()
    assert isinstance(exported_info, supervisor_core.WorkerInfo)
    assert exported_info.worker_address == f"localhost:{self.port}"
    assert exported_info.local_rank == self.local_rank
    assert exported_info.global_rank == self.global_rank
    assert exported_info.worker_id == "0000:01:00.0"

  def test_update_info(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    new_info = supervisor_core.WorkerInfo(global_rank=5)
    client.update_info(new_info)
    assert client.global_rank == 5

  def test_send_heartbeat(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    client.send_heartbeat()
    self.mock_worker_instance.send_heartbeat.assert_called_once()

  def test_export_workload_info(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    workload_info = client.export_workload_info()
    assert isinstance(workload_info, supervisor_core.WorkloadInfo)
    assert workload_info.workload_name == self.workload_name
    assert workload_info.job_name == self.job_name
    assert workload_info.container_name == self.container_name
    assert workload_info.num_data_replicas == self.num_data_replicas
    assert workload_info.max_num_data_replicas == self.max_num_data_replicas
    assert workload_info.min_num_data_replicas == self.min_num_data_replicas
    assert (
        workload_info.num_nodes_per_data_replica
        == self.num_nodes_per_data_replica
    )
    assert (
        workload_info.container_termination_threshold_s
        == self.container_termination_threshold_s
    )
    assert (
        workload_info.workload_downtime_threshold_s
        == self.workload_downtime_threshold_s
    )
    assert workload_info.max_in_job_restarts == self.max_in_job_restarts
    assert workload_info.max_workload_restarts == self.max_workload_restarts
    assert (
        workload_info.workload_scaling_enabled == self.workload_scaling_enabled
    )

  def test_update_workload_info(self):
    client = workload.GoogleCloudResiliencyClient(
        port=self.port,
        host_port=self.host_port,
        local_rank=self.local_rank,
        global_rank=self.global_rank,
        workload_name=self.workload_name,
        job_name=self.job_name,
        container_name=self.container_name,
        num_data_replicas=self.num_data_replicas,
        max_num_data_replicas=self.max_num_data_replicas,
        min_num_data_replicas=self.min_num_data_replicas,
        num_nodes_per_data_replica=self.num_nodes_per_data_replica,
        container_termination_threshold_s=self.container_termination_threshold_s,
        workload_downtime_threshold_s=self.workload_downtime_threshold_s,
        max_in_job_restarts=self.max_in_job_restarts,
        max_workload_restarts=self.max_workload_restarts,
        workload_scaling_enabled=self.workload_scaling_enabled,
    )
    supervisor_core_workload_info = supervisor_core.WorkloadInfo()
    supervisor_core_workload_info.workload_scaling_enabled = True
    client.update_workload_info(supervisor_core_workload_info)
    assert client.workload_scaling_enabled


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
