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
import random
import time

import numpy as np
from numpy import typing
from simulator.python import base_simulator
from simulator.python import gpu_failure_simulator


XIDs = {
    43: "Graphics Engine Hang",
    48: "Double bit ECC error",
    53: "Fatal, Link 00 TSID Error",
    79: "Graphics Engine Error",
    94: "Contained: SM (0x1). (pid 0), RST: No, D-RSTL No",
}


class XIDSimulator(base_simulator.BaseSimulator):
  """Simulates periodic XID errors and optional continuous GPU crashing."""

  def __init__(
      self,
      rank: int,
      gpu_world_size: int,
      gpus_per_node: int = 8,
      seed: int = 42,
  ):
    """Initializes the XIDSimulator.

    Args:
        rank: The rank of the VM running the simulator.
        gpu_world_size: The total number of GPUs in the distributed environment.
        gpus_per_node: The number of GPUs per node. Defaults to 8.
        seed: The seed for the random number generator. Defaults to 42.
    """
    super().__init__(rank, gpu_world_size, gpus_per_node, seed)

    self.logger = base_simulator.setup_logger()
    self.logger.info("Initializing XID simulator.")

    self._gpu_failure_simulator = gpu_failure_simulator.GPUFailureSimulator(
        rank, gpu_world_size, gpus_per_node, seed
    )

  def _get_pci_bus_id_for_local_gpu(self, local_gpu_idx: int) -> str:
    """Generates a simulated PCI bus ID string for a local GPU."""
    get_pci_bus_id = base_simulator.get_pci_bus_id(
        local_gpu_idx, use_nsenter=False
    )
    return get_pci_bus_id

  def _inject_xid_error(
      self,
      local_gpu_idx: int,
      xid_code: int,
      should_crash: bool = False,
  ) -> None:
    """Simulates an XID error for a local GPU.

    Args:
        local_gpu_idx: The local index of the GPU on the current node. If None,
          a random local GPU is chosen.
        xid_code: The XID code for this specific event. If None, uses instance
          default.
    """
    xid_reason = XIDs[xid_code]
    pci_bus_id = self._get_pci_bus_id_for_local_gpu(local_gpu_idx)
    global_rank_affected = self.rank * self.gpus_per_node + local_gpu_idx

    error_message = f"NVRM: Xid (PCI:{pci_bus_id}): {xid_code}, {xid_reason}"
    self.logger.info(f"Simulating XID error: {error_message}")

    # Simulate the XID error by writing the error message to the kernel log.
    os.system(f'echo "{error_message}" > /dev/kmsg')

    if should_crash:
      self._crash_gpu(global_rank_affected)

  def _crash_gpu(self, global_gpu_rank: int):
    """Determines which GPUs are currently in a "crashed" state due to XID errors.

    Args:
        global_gpu_rank: The global rank of the GPU on the current node.
    """
    self._gpu_failure_simulator.induce_event([global_gpu_rank])

  def sample(self, lambda_value: float) -> typing.NDArray[bool]:
    """Samples for XID events on local GPUs based on the Poisson distribution.

    Args:
        lambda_value (float): The lambda value (expected number of events) for
          the node for the current sample interval.

    Returns:
        np.ndarray[bool]: A boolean array indicating which local GPUs
                          have experienced an XID event.
    """
    probabilities = self.distribution(lambda_value, self.gpus_per_node)
    random_numbers = self._rng.random(self.gpus_per_node)
    return random_numbers < probabilities

  def simulate(
      self, mtbf_node_years: float, sample_interval_seconds: int
  ) -> None:
    """Starts the XID error simulation loop using Poisson point process.

    Args:
        mtbf_node_years: Mean Time Between XID Failures (for any GPU on the
          node) in years.
        sample_interval_seconds: The interval in seconds between samples.
    """
    if mtbf_node_years <= 0:
      self.logger.info(
          f"XIDSimulator (Rank {self.rank}): MTBF is non-positive"
          f" ({mtbf_node_years}), so no XID events will be simulated."
      )
      return

    mtbf_node_seconds = mtbf_node_years * 365 * 24 * 3600
    # Lambda is the expected number of XID events on this node per sample_interval
    lambda_value = (1.0 / mtbf_node_seconds) * sample_interval_seconds

    self.logger.info(
        f"XIDSimulator (Rank {self.rank}): Starting simulation with MTBF"
        f" (node): {mtbf_node_years} years, sample interval:"
        f" {sample_interval_seconds}s, lambda (node per interval):"
        f" {lambda_value:.6e}."
    )

    while not self.is_completed():
      try:
        local_gpus_xid_flags = self.sample(lambda_value)
        affected_local_indices = np.where(local_gpus_xid_flags)[0]
        global_gpu_ranks_affected = self.local_to_global_ranks(
            affected_local_indices
        )

        if affected_local_indices.size > 0:
          self.logger.info(
              f"XIDSimulator (Rank {self.rank}): Sampled XID event(s) for local"
              f" GPU(s): {affected_local_indices}."
          )
        for global_gpu_rank in global_gpu_ranks_affected:
          xid_code = random.choice(list(XIDs.keys()))
          should_crash = self._rng.random() < 0.5

          self.induce_event(
              global_ranks=[global_gpu_rank],
              xid_code=xid_code,
              should_crash=should_crash,
          )

        time.sleep(sample_interval_seconds)
      except KeyboardInterrupt:
        self.logger.info(
            f"XIDSimulator (Rank {self.rank}): Simulation interrupted by user."
        )
        break
      except Exception as e:
        self.logger.info(
            f"XIDSimulator (Rank {self.rank}): Error during simulation: {e}"
        )
        break

    self.logger.info(f"XIDSimulator (Rank {self.rank}): Simulation finished.")

  def induce_event(
      self,
      global_ranks: list[int],
      xid_code: int | None = None,
      should_crash: bool = False,
  ) -> None:
    """Induces an XID error deterministically on a specified global GPU rank.

    Args:
        global_ranks: The global ranks of the GPUs to affect.
        xid_code: Optional specific XID code for this event. If None, uses
          instance default.
        should_crash: Whether to crash the GPU after inducing the XID error.
    """
    if xid_code is None or xid_code not in XIDs:
      xid_code = random.choice(list(XIDs.keys()))

    # Only induce events on GPUs within the current VM
    global_ranks = self.filter_global_ranks(global_ranks)
    local_ranks = self.global_to_local_ranks(global_ranks)

    for i, local_gpu_idx in enumerate(local_ranks):
      self.logger.info(
          f"XIDSimulator (Rank {self.rank}): Inducing XID event for"
          f" global_gpu_rank {global_ranks[i]} (local_gpu_idx {local_gpu_idx})."
      )
      self._inject_xid_error(
          local_gpu_idx=local_gpu_idx,
          xid_code=xid_code,
          should_crash=should_crash,
      )
