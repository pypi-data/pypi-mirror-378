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

import subprocess
import sys
import threading
import time
from unittest import mock

import numpy as np
import pytest
from simulator.python import base_simulator
from simulator.python import gpu_slowdown_simulator


@pytest.fixture
def simulator():
  """Fixture to create a GPUSlowdownSimulator instance."""
  rank = 0
  gpu_world_size = 8
  gpus_per_node = 8
  seed = 42
  return gpu_slowdown_simulator.GPUSlowdownSimulator(
      rank=rank,
      gpu_world_size=gpu_world_size,
      gpus_per_node=gpus_per_node,
      seed=seed,
  )


@pytest.fixture
def mock_subprocess_run():
  """Fixture to mock subprocess.run."""
  with mock.patch.object(subprocess, "run", autospec=True) as mock_fn:
    yield mock_fn


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
  assert not simulator._slow_gpus  # pylint: disable=protected-access


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


def test_gpu_slowdown_fn(simulator, mock_subprocess_run):  # pylint: disable=redefined-outer-name
  local_ranks = [0, 2]
  simulator._gpu_slowdown_fn(local_ranks, gpu_power_limit=150)  # pylint: disable=protected-access

  mock_subprocess_run.assert_called_once_with(
      [
          "nvidia-smi",
          "-pl",
          "150",
          "-i",
          "0,2",
      ],
      capture_output=True,
      check=True,
      shell=False,
      text=True,
  )
  assert 0 in simulator._slow_gpus  # pylint: disable=protected-access
  assert 2 in simulator._slow_gpus  # pylint: disable=protected-access


def test_gpu_slowdown_fn_with_error(simulator, mock_subprocess_run):  # pylint: disable=redefined-outer-name
  local_ranks = [0, 2]
  mock_subprocess_run.side_effect = subprocess.CalledProcessError(
      returncode=1, cmd="test", stderr="error"
  )
  simulator._gpu_slowdown_fn(local_ranks)  # pylint: disable=protected-access
  mock_subprocess_run.assert_called_once()
  assert not simulator._slow_gpus  # pylint: disable=protected-access


def test_gpu_reset_fn_with_local_ranks(simulator, mock_subprocess_run):  # pylint: disable=redefined-outer-name
  simulator._slow_gpus = {0: (10, 0), 2: (10, 0)}  # pylint: disable=protected-access
  local_ranks = [0, 2]
  simulator._gpu_reset_fn(local_ranks)  # pylint: disable=protected-access

  mock_subprocess_run.assert_called_once_with(
      [
          "nvidia-smi",
          "-pl",
          "700",
          "-i",
          "0,2",
      ],
      capture_output=True,
      check=True,
      shell=False,
      text=True,
  )
  assert not simulator._slow_gpus  # pylint: disable=protected-access


def test_gpu_reset_fn_without_local_ranks(simulator, mock_subprocess_run):  # pylint: disable=redefined-outer-name
  simulator._slow_gpus = {0: (10, 0), 2: (10, 0)}  # pylint: disable=protected-access
  simulator._gpu_reset_fn()  # pylint: disable=protected-access

  mock_subprocess_run.assert_called_once_with(
      [
          "nvidia-smi",
          "-pl",
          "700",
      ],
      capture_output=True,
      check=True,
      shell=False,
      text=True,
  )
  assert not simulator._slow_gpus  # pylint: disable=protected-access


def test_gpu_reset_fn_with_error(simulator, mock_subprocess_run):  # pylint: disable=redefined-outer-name
  mock_subprocess_run.side_effect = subprocess.CalledProcessError(
      returncode=1, cmd="test", stderr="error"
  )
  simulator._gpu_reset_fn()  # pylint: disable=protected-access
  mock_subprocess_run.assert_called_once()


def test_induce_event(simulator):  # pylint: disable=redefined-outer-name
  global_ranks = [0, 2, 8, 10]
  with mock.patch.object(simulator, "_gpu_slowdown_fn") as mock_gpu_slowdown_fn:
    simulator.induce_event(global_ranks, gpu_power_limit=250)
    mock_gpu_slowdown_fn.assert_called_with([0, 2], 300, 250)


def test_induce_event_duration(simulator):  # pylint: disable=redefined-outer-name
  global_ranks = [0, 2, 8, 10]
  simulator._slow_gpus = {0: (5, time.monotonic() - 5)}  # pylint: disable=protected-access
  with mock.patch.object(simulator, "_gpu_reset_fn") as mock_gpu_reset_fn:
    with mock.patch.object(
        simulator, "_gpu_slowdown_fn"
    ) as mock_gpu_slowdown_fn:
      simulator.induce_event(global_ranks, gpu_power_limit=250)
      mock_gpu_slowdown_fn.assert_has_calls([mock.call([2], 300, 250)])
      time.sleep(5)
      mock_gpu_reset_fn.assert_called_with([0])


def test_simulate(
    simulator, mock_subprocess_run, mock_check_termination_file, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
):
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
      mock_sample.assert_called()
      mock_induce_event.assert_called_with(
          [0, 2, 4, 6], duration=300, gpu_power_limit=200
      )
      mock_time_sleep.assert_called_with(sample_interval)
  mock_subprocess_run.assert_called_with(
      [
          "nvidia-smi",
          "-pl",
          "700",
      ],
      capture_output=True,
      check=True,
      shell=False,
      text=True,
  )


def test_simulate_async(
    simulator, mock_subprocess_run, mock_check_termination_file, mock_thread, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
):
  mtbf = 1.0
  sample_interval = 1

  with mock.patch.object(
      simulator, "induce_event", autospec=True
  ) as mock_induce_event:
    simulator.simulate(mtbf, sample_interval, run_async=True)
    mock_induce_event.assert_not_called()

  mock_thread.assert_called_once()
  mock_thread.return_value.start.assert_called_once()


def test_simulate_with_mutex(
    simulator, mock_subprocess_run, mock_check_termination_file, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
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
      mock_induce_event.assert_called()


def test_simulate_with_termination_file(
    simulator, mock_subprocess_run, mock_check_termination_file, mock_time_sleep  # pylint: disable=redefined-outer-name,unused-argument
):
  mtbf = 1.0
  sample_interval = 1
  with mock.patch.object(simulator, "sample") as mock_sample:
    simulator.simulate(mtbf, sample_interval)
    assert mock_sample.call_count == 2


def test_simulate_with_invalid_power_limit(simulator):  # pylint: disable=redefined-outer-name
  mtbf = 1.0
  sample_interval = 1
  with pytest.raises(ValueError):
    simulator.simulate(mtbf, sample_interval, gpu_power_limit=50)


def test_induce_event_with_invalid_power_limit(simulator):  # pylint: disable=redefined-outer-name
  with pytest.raises(ValueError):
    simulator.induce_event([0], gpu_power_limit=50)


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
