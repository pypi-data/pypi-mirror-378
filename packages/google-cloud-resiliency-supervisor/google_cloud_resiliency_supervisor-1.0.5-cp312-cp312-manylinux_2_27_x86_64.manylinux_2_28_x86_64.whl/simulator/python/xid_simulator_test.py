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
import os
import random
import sys
import time
from unittest import mock

import numpy as np
import pytest
from simulator.python import base_simulator
from simulator.python import gpu_failure_simulator
from simulator.python import xid_simulator


@pytest.fixture
def mock_gpu_failure_simulator():
  """Fixture to mock GPUFailureSimulator."""
  with mock.patch.object(
      gpu_failure_simulator, "GPUFailureSimulator", autospec=True
  ) as mock_sim:
    yield mock_sim


@pytest.fixture
def simulator(mock_gpu_failure_simulator):  # pylint: disable=redefined-outer-name, unused-argument
  """Fixture to create a XIDSimulator instance."""
  rank = 0
  gpu_world_size = 8
  gpus_per_node = 8
  seed = 42
  return xid_simulator.XIDSimulator(
      rank=rank,
      gpu_world_size=gpu_world_size,
      gpus_per_node=gpus_per_node,
      seed=seed,
  )


@pytest.fixture
def mock_get_pci_bus_id():
  """Fixture to mock base_simulator.get_pci_bus_id."""
  with mock.patch.object(
      base_simulator, "get_pci_bus_id", autospec=True
  ) as mock_fn:
    mock_fn.return_value = "0000:00:04.0"
    yield mock_fn


@pytest.fixture
def mock_system():
  """Fixture to mock os.system."""
  with mock.patch.object(os, "system", autospec=True) as mock_fn:
    yield mock_fn


@pytest.fixture
def mock_time_sleep():
  """Fixture to mock time.sleep."""
  with mock.patch.object(time, "sleep", autospec=True) as mock_sleep:
    yield mock_sleep


@pytest.fixture
def mock_random_choice():
  """Fixture to mock random.choice."""
  with mock.patch.object(random, "choice", autospec=True) as mock_choice:
    # Ensure it returns a valid key from xid_simulator.XIDs
    mock_choice.return_value = list(xid_simulator.XIDs.keys())[0]
    yield mock_choice


@pytest.fixture
def mock_is_completed():
  """Fixture to mock XIDSimulator.is_completed."""
  # Simulate loop running twice then terminating
  with mock.patch.object(
      xid_simulator.XIDSimulator,
      "is_completed",
      autospec=True,
      side_effect=[False, False, True],
  ) as mock_fn:
    yield mock_fn


def test_init(simulator, mock_gpu_failure_simulator):  # pylint: disable=redefined-outer-name
  """Tests the initialization of the XIDSimulator."""
  assert simulator.rank == 0
  assert simulator.gpu_world_size == 8
  assert simulator.gpus_per_node == 8
  assert simulator.seed == 42
  mock_gpu_failure_simulator.assert_called_once_with(0, 8, 8, 42)
  assert simulator.logger.level == logging.INFO  # pylint: disable=protected-access


def test_get_pci_bus_id_for_local_gpu(simulator, mock_get_pci_bus_id):  # pylint: disable=redefined-outer-name
  """Tests the _get_pci_bus_id_for_local_gpu method."""
  local_gpu_idx = 1
  pci_id = simulator._get_pci_bus_id_for_local_gpu(local_gpu_idx)  # pylint: disable=protected-access
  mock_get_pci_bus_id.assert_called_once_with(local_gpu_idx, use_nsenter=False)
  assert pci_id == "0000:00:04.0"


def test_inject_xid_error_no_crash(simulator, mock_get_pci_bus_id, mock_system):  # pylint: disable=redefined-outer-name
  """Tests _inject_xid_error without crashing the GPU."""
  local_gpu_idx = 0
  xid_code = 43
  # Ensure _crash_gpu is not called if should_crash is False
  with mock.patch.object(simulator, "_crash_gpu") as mock_crash_gpu:
    simulator._inject_xid_error(local_gpu_idx, xid_code, should_crash=False)  # pylint: disable=protected-access

    mock_get_pci_bus_id.assert_called_once_with(
        local_gpu_idx, use_nsenter=False
    )
    expected_pci_id = "0000:00:04.0"
    expected_xid_reason = xid_simulator.XIDs[xid_code]
    expected_error_message = (
        f"NVRM: Xid (PCI:{expected_pci_id}): {xid_code}, {expected_xid_reason}"
    )
    mock_system.assert_called_once_with(
        f'echo "{expected_error_message}" > /dev/kmsg'
    )
    mock_crash_gpu.assert_not_called()


def test_inject_xid_error_with_crash(simulator, mock_get_pci_bus_id, mock_system):  # pylint: disable=redefined-outer-name
  """Tests _inject_xid_error with crashing the GPU."""
  local_gpu_idx = 1
  xid_code = 48
  global_rank_affected = (
      simulator.rank * simulator.gpus_per_node + local_gpu_idx
  )
  with mock.patch.object(simulator, "_crash_gpu") as mock_crash_gpu:
    simulator._inject_xid_error(local_gpu_idx, xid_code, should_crash=True)  # pylint: disable=protected-access

    mock_get_pci_bus_id.assert_called_once_with(
        local_gpu_idx, use_nsenter=False
    )
    mock_system.assert_called_once()
    mock_crash_gpu.assert_called_once_with(global_rank_affected)


def test_crash_gpu(simulator):  # pylint: disable=redefined-outer-name
  """Tests the _crash_gpu method."""
  global_gpu_rank = 3
  simulator._crash_gpu(global_gpu_rank)  # pylint: disable=protected-access
  simulator._gpu_failure_simulator.induce_event.assert_called_once_with(  # pylint: disable=protected-access
      [global_gpu_rank]
  )


def test_sample(simulator):  # pylint: disable=redefined-outer-name
  """Tests the sample method."""
  lambda_value = 0.5
  # Mock the distribution to control its output
  with mock.patch.object(
      simulator,
      "distribution",
      return_value=np.array([0.6, 0.2, 0.8, 0.1, 0.5, 0.9, 0.3, 0.7]),
  ):
    # Mock the random number generator for predictable results
    mock_rng = mock.Mock()
    mock_rng.random = mock.Mock(
        return_value=np.array([0.5, 0.3, 0.7, 0.2, 0.6, 0.8, 0.4, 0.6])
    )
    simulator._rng = mock_rng  # pylint: disable=protected-access

    result = simulator.sample(lambda_value)
    assert isinstance(result, np.ndarray)
    assert result.dtype == bool
    assert result.size == simulator.gpus_per_node
    expected_result = np.array(
        [True, False, True, False, False, True, False, True]
    )
    np.testing.assert_array_equal(result, expected_result)
    simulator.distribution.assert_called_once_with(
        lambda_value, simulator.gpus_per_node
    )


def test_induce_event_specific_xid(simulator, mock_random_choice):  # pylint: disable=redefined-outer-name
  """Tests induce_event with a specific XID code."""
  global_gpu_rank = 2  # Belongs to current rank 0
  xid_code = 79
  should_crash = True

  with mock.patch.object(simulator, "_inject_xid_error") as mock_inject:
    simulator.induce_event([global_gpu_rank], xid_code, should_crash)
    # global_gpu_rank 2 -> local_gpu_idx 2 for rank 0
    mock_inject.assert_called_once_with(
        local_gpu_idx=2, xid_code=xid_code, should_crash=should_crash
    )
    mock_random_choice.assert_not_called()


def test_induce_event_random_xid(simulator, mock_random_choice):  # pylint: disable=redefined-outer-name
  """Tests induce_event with a random XID code."""
  global_gpu_rank = 5  # Belongs to current rank 0
  should_crash = False
  expected_random_xid = list(xid_simulator.XIDs.keys())[0]

  with mock.patch.object(simulator, "_inject_xid_error") as mock_inject:
    simulator.induce_event(
        [global_gpu_rank], xid_code=None, should_crash=should_crash
    )
    # global_gpu_rank 5 -> local_gpu_idx 5 for rank 0
    mock_inject.assert_called_once_with(
        local_gpu_idx=5, xid_code=expected_random_xid, should_crash=should_crash
    )
    mock_random_choice.assert_called_once_with(list(xid_simulator.XIDs.keys()))


def test_induce_event_invalid_xid_uses_random(simulator, mock_random_choice):  # pylint: disable=redefined-outer-name
  """Tests induce_event with an invalid XID code, expecting it to use a random one."""
  global_gpu_rank = 1
  invalid_xid_code = 9999
  should_crash = False
  expected_random_xid = list(xid_simulator.XIDs.keys())[0]

  with mock.patch.object(simulator, "_inject_xid_error") as mock_inject:
    simulator.induce_event([global_gpu_rank], invalid_xid_code, should_crash)
    mock_inject.assert_called_once_with(
        local_gpu_idx=1, xid_code=expected_random_xid, should_crash=should_crash
    )
    mock_random_choice.assert_called_once_with(list(xid_simulator.XIDs.keys()))


def test_induce_event_other_node_rank(simulator, mock_random_choice):  # pylint: disable=redefined-outer-name
  """Tests induce_event for a GPU on another node (should not inject)."""
  global_gpu_rank = 10  # Does not belong to current rank 0 (gpus_per_node=8)
  with mock.patch.object(simulator, "_inject_xid_error") as mock_inject:
    simulator.induce_event([global_gpu_rank], xid_code=43)
    mock_inject.assert_not_called()
    mock_random_choice.assert_not_called()  # xid_code was provided


def test_simulate_mtbf_non_positive(simulator, mock_time_sleep, mock_is_completed):  # pylint: disable=redefined-outer-name
  """Tests simulate when mtbf_node_years is non-positive."""
  with mock.patch.object(simulator, "sample") as mock_sample:
    with mock.patch.object(simulator, "induce_event") as mock_induce_event:
      simulator.simulate(mtbf_node_years=0, sample_interval_seconds=10)
      mock_sample.assert_not_called()
      mock_induce_event.assert_not_called()
      mock_time_sleep.assert_not_called()
      mock_is_completed.assert_not_called()  # Loop should not start


def test_simulate_loop(simulator, mock_time_sleep, mock_is_completed, mock_random_choice):  # pylint: disable=redefined-outer-name, unused-argument
  """Tests the main simulation loop."""
  mtbf_node_years = 1.0
  sample_interval_seconds = 10
  # Expected lambda: (1.0 / (1.0 * 365 * 24 * 3600)) * 10

  # Mock sample to return specific events
  # First call: GPU 0 and 2 have XID events
  # Second call: GPU 1 has an XID event
  mock_sample_returns = [
      np.array([True, False, True, False, False, False, False, False]),
      np.array([False, True, False, False, False, False, False, False]),
  ]
  # Mock RNG for should_crash decision (True, False, True for the 3 events)
  mock_rng = mock.Mock()
  mock_rng.random = mock.Mock(side_effect=[0.2, 0.7, 0.3])  # <0.5 means crash
  simulator._rng = mock_rng  # pylint: disable=protected-access

  with mock.patch.object(
      simulator, "sample", side_effect=mock_sample_returns
  ) as mock_sample:
    with mock.patch.object(simulator, "induce_event") as mock_induce_event:
      simulator.simulate(mtbf_node_years, sample_interval_seconds)

      assert mock_sample.call_count == 2
      assert mock_induce_event.call_count == 3
      expected_xid = list(xid_simulator.XIDs.keys())[
          0
      ]  # from mock_random_choice

      # Call 1 from sample 1 (local GPU 0, global 0)
      mock_induce_event.assert_any_call(
          global_ranks=[0], xid_code=expected_xid, should_crash=True
      )
      # Call 2 from sample 1 (local GPU 2, global 2)
      mock_induce_event.assert_any_call(
          global_ranks=[2], xid_code=expected_xid, should_crash=False
      )
      # Call 3 from sample 2 (local GPU 1, global 1)
      mock_induce_event.assert_any_call(
          global_ranks=[1], xid_code=expected_xid, should_crash=True
      )

      assert mock_time_sleep.call_count == 2
      mock_time_sleep.assert_called_with(sample_interval_seconds)
      assert mock_is_completed.call_count == 3  # Called until True


def test_simulate_keyboard_interrupt(simulator, mock_time_sleep, mock_is_completed):  # pylint: disable=redefined-outer-name
  """Tests that KeyboardInterrupt stops the simulation."""
  mtbf_node_years = 1.0
  sample_interval_seconds = 10
  mock_is_completed.side_effect = [False, False, False]  # Keep running
  mock_time_sleep.side_effect = KeyboardInterrupt  # Interrupt on first sleep

  with mock.patch.object(
      simulator, "sample", return_value=np.array([False] * 8)
  ) as mock_sample:
    with mock.patch.object(simulator, "induce_event") as mock_induce_event:
      simulator.simulate(mtbf_node_years, sample_interval_seconds)
      mock_sample.assert_called_once()  # Loop runs once before interrupt
      mock_induce_event.assert_not_called()  # No events sampled
      mock_time_sleep.assert_called_once_with(sample_interval_seconds)
      # is_completed is checked at the start of each loop
      assert mock_is_completed.call_count == 1


def test_simulate_generic_exception(simulator, mock_time_sleep, mock_is_completed):  # pylint: disable=redefined-outer-name
  """Tests that a generic exception stops the simulation."""
  mtbf_node_years = 1.0
  sample_interval_seconds = 10
  mock_is_completed.side_effect = [False, False, False]  # Keep running
  mock_time_sleep.side_effect = ValueError("Test Error")  # Error on first sleep

  with mock.patch.object(
      simulator, "sample", return_value=np.array([False] * 8)
  ) as mock_sample:
    with mock.patch.object(simulator, "induce_event") as mock_induce_event:
      simulator.simulate(mtbf_node_years, sample_interval_seconds)
      mock_sample.assert_called_once()
      mock_induce_event.assert_not_called()
      mock_time_sleep.assert_called_once_with(sample_interval_seconds)
      assert mock_is_completed.call_count == 1


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
