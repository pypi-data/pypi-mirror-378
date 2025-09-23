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

import logging
import subprocess
import sys
import threading
import time
from unittest import mock

import numpy as np
import pytest
from simulator.python import base_simulator
from simulator.python import gpu_failure_simulator


@pytest.fixture
def simulator():
  """Fixture to create a GPUFailureSimulator instance."""
  rank = 0
  gpu_world_size = 8
  gpus_per_node = 8
  seed = 42
  return gpu_failure_simulator.GPUFailureSimulator(
      rank=rank,
      gpu_world_size=gpu_world_size,
      gpus_per_node=gpus_per_node,
      seed=seed,
  )


@pytest.fixture
def mock_check_termination_file():
  """Fixture to mock check_termination_file."""
  with mock.patch.object(
      base_simulator,
      "check_termination_file",
      autospec=True,
      side_effect=[False, False, True],
  ) as mock_fn:
    yield mock_fn


@pytest.fixture
def mock_thread():
  """Fixture to mock threading.Thread."""
  with mock.patch.object(threading, "Thread", autospec=True) as mock_t:
    yield mock_t


@pytest.fixture
def mock_time_sleep():
  """Fixture to mock time.sleep."""
  with mock.patch.object(time, "sleep", autospec=True) as mock_sleep:
    yield mock_sleep


def test_init(simulator):  # pylint: disable=redefined-outer-name
  assert simulator.rank == 0
  assert simulator.gpu_world_size == 8
  assert simulator.gpus_per_node == 8
  assert simulator.seed == 42


def test_sample(simulator):  # pylint: disable=redefined-outer-name
  lambda_value = 0.5
  with mock.patch.object(
      simulator,
      "distribution",
      return_value=np.array([0.6, 0.2, 0.8, 0.1, 0.5, 0.9, 0.3, 0.7]),
  ):
    result = simulator.sample(lambda_value)
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert result.size == simulator.gpus_per_node


@mock.patch("subprocess.run")
def test_gpu_kill_fn(mock_run, simulator):  # pylint: disable=redefined-outer-name
  local_ranks = [0, 2]
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="1234, python\n5678, other_process",
  )
  simulator._gpu_kill_fn(local_ranks)  # pylint: disable=protected-access

  mock_run.assert_has_calls([
      mock.call(
          [
              "nvidia-smi",
              "--query-compute-apps",
              "pid,name",
              "--format=csv,noheader",
              "-i",
              "0",
          ],
          capture_output=True,
          check=True,
          shell=False,
          text=True,
      ),
      mock.call(
          [
              "kill",
              "-9",
              "1234",
          ],
          capture_output=True,
          check=True,
          shell=False,
          text=True,
      ),
      mock.call(
          [
              "nvidia-smi",
              "--query-compute-apps",
              "pid,name",
              "--format=csv,noheader",
              "-i",
              "2",
          ],
          capture_output=True,
          check=True,
          shell=False,
          text=True,
      ),
      mock.call(
          [
              "kill",
              "-9",
              "1234",
          ],
          capture_output=True,
          check=True,
          shell=False,
          text=True,
      ),
  ])


@mock.patch("subprocess.run")
def test_gpu_kill_fn_with_error(mock_run, simulator, caplog):  # pylint: disable=redefined-outer-name
  local_ranks = [6]
  mock_run.side_effect = subprocess.CalledProcessError(
      returncode=1, cmd="test", stderr="error"
  )
  caplog.set_level(logging.WARNING)
  simulator.logger = logging.getLogger(__name__)
  simulator.logger.setLevel(logging.WARNING)

  simulator._gpu_kill_fn(local_ranks)  # pylint: disable=protected-access
  mock_run.assert_called_once()
  assert (
      "Command nvidia-smi --query-compute-apps pid,name --format=csv,noheader"
      " -i 6 failed with error."
      in caplog.text
  )


def test_induce_event(simulator):  # pylint: disable=redefined-outer-name
  global_ranks = [
      0,
      2,
      8,
      10,
  ]  # Ranks for current VM: [0, 1, 2, 3, 4, 5, 6, 7]
  with mock.patch.object(simulator, "_gpu_kill_fn") as mock_gpu_kill_fn:
    simulator.induce_event(global_ranks)
    mock_gpu_kill_fn.assert_called_with([0, 2])


def test_simulate(simulator, mock_check_termination_file, mock_time_sleep):  # pylint: disable=redefined-outer-name,unused-argument
  mtbf = 1.0
  sample_interval = 1
  with mock.patch.object(
      simulator,
      "sample",
      return_value=np.array(
          [True, False, True, False, True, False, True, False]
      ),
  ) as mock_sample:
    with mock.patch.object(simulator, "induce_event") as mock_induce_event:
      simulator.simulate(mtbf, sample_interval)
      assert mock_sample.call_count == 2
      mock_induce_event.assert_called_with([0, 2, 4, 6])
      assert mock_time_sleep.call_count == 2
      mock_time_sleep.assert_called_with(sample_interval)


def test_simulate_async(
    simulator, mock_check_termination_file, mock_thread, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
):
  mtbf = 1.0
  sample_interval = 1
  simulator.simulate(mtbf, sample_interval, run_async=True)
  mock_thread.assert_called_once()
  mock_thread.return_value.start.assert_called_once()


def test_simulate_with_mutex(
    simulator, mock_check_termination_file, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
):
  mtbf = 1.0
  sample_interval = 1
  mutex = threading.Lock()
  with mock.patch.object(
      simulator,
      "sample",
      return_value=np.array(
          [True, False, True, False, True, False, True, False]
      ),
  ):
    with mock.patch.object(simulator, "induce_event") as mock_induce_event:
      simulator.simulate(mtbf, sample_interval, mutex=mutex)
      assert mock_induce_event.call_count == 2
      assert mock_time_sleep.call_count == 2


def test_simulate_with_termination_file(
    simulator, mock_check_termination_file, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
):
  mtbf = 1.0
  sample_interval = 1
  with mock.patch.object(simulator, "sample") as mock_sample:
    simulator.simulate(mtbf, sample_interval)
    assert mock_sample.call_count == 2
    assert mock_time_sleep.call_count == 2


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
