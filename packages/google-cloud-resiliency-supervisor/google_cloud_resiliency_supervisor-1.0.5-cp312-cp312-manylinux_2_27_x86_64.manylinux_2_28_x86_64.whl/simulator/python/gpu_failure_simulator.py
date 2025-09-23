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

import contextlib
import random
import subprocess
import threading
import time
import numpy as np
from numpy import typing
from simulator.python import base_simulator


class GPUFailureSimulator(base_simulator.BaseSimulator):
  """Simulates GPU failures in a distributed training environment.

  This class simulates GPU failures by randomly killing processes running on
  GPUs based on a given Mean Time Between Failures (MTBF). It uses a Poisson
  distribution to model the failure probability.
  """

  def __init__(
      self,
      rank: int,
      gpu_world_size: int,
      gpus_per_node: int = 8,
      seed: int = 42,
  ):
    """Initializes instance of FailureSimulator.

    Args:
        rank (int): The rank of the VM running the simulator.
        gpu_world_size (int): The total number of GPUs in the distributed
          environment.
        gpus_per_node (int, optional): The number of GPUs per node. Defaults to
          8.
        seed (int, optional): The seed for the random number generator. Defaults
          to 42.
    """
    super().__init__(rank, gpu_world_size, gpus_per_node, seed)
    self.logger = base_simulator.setup_logger()
    self.logger.info("Initializing GPU failure simulator.")

  def _gpu_kill_fn(self, local_ranks: list[int]):
    """Kills the processes running on GPUs on specified local ranks.

    Args:
        local_ranks (list[int]): The ranks of GPUs to be killed.
    """
    for rank in local_ranks:
      self.logger.info(f"Killing a process on GPU with local rank: {rank}.")

      get_pids_cmd = (
          "nvidia-smi --query-compute-apps pid,name --format=csv,noheader -i"
          f" {rank}"
      )

      try:
        result = subprocess.run(
            get_pids_cmd.split(),
            capture_output=True,
            check=True,
            shell=False,
            text=True,
        )

        processes = result.stdout.splitlines()
        pid = random.choice([
            process.split(", ")[0]
            for process in processes
            if "python" in process or "tcpgpudmarxd" in process
        ])

        pkill_cmd = f"kill -9 {pid}"
        self.logger.info(f"Killing process: {pkill_cmd}")

        subprocess.run(
            pkill_cmd.split(),
            capture_output=True,
            shell=False,
            check=True,
            text=True,
        )
      except subprocess.CalledProcessError as e:
        self.logger.warning(f"Command {get_pids_cmd} failed with {e.stderr}.")

  def sample(self, lambda_value: float) -> typing.NDArray[bool]:
    """Samples for GPU failures based on the Poisson distribution.

    Args:
        lambda_value (float): The lambda value of the Poisson distribution.

    Returns:
        np.ndarray[bool]: A boolean array indicating which GPUs have failed.
    """
    random_numbers = np.random.rand(self.gpus_per_node)
    probabilities = self.distribution(lambda_value, self.gpus_per_node)
    return random_numbers < probabilities

  def simulate(
      self,
      mtbf: float,
      sample_interval: int,
      run_async: bool = False,
      mutex: type(threading.Lock()) | None = None,
  ):
    """Starts the failure simulation loop.

    This method continuously samples for failures and simulates them by killing
    the corresponding processes running on the failed GPUs. It runs until a
    termination file is detected.

    Args:
        mtbf (float): The Mean Time Between Failures (MTBF) in years.
        sample_interval (int): The interval in seconds between samples.
        run_async (bool): Whether to run the simulation asynchronously. Defaults
          to False.
        mutex (LockType): Optional mutex to synchronize multiple simulatenous
          simulators. Defaults to None.
    """
    mtbf_s = mtbf * 365 * 24 * 3600
    lambda_value = (1 / mtbf_s) * sample_interval
    mutex = mutex if mutex is not None else contextlib.nullcontext()

    self.logger.info(
        f"Starting simulation loop with MTBF: {mtbf} years and sample interval:"
        f" {sample_interval} seconds."
    )

    def simulate_loop():
      while not self.is_completed():
        failure_events = self.sample(lambda_value)
        if failure_events.any():
          with mutex:
            failure_ranks = np.where(failure_events)[0].tolist()
            global_ranks = self.local_to_global_ranks(failure_ranks)
            self.induce_event(global_ranks)

        time.sleep(sample_interval)

    if run_async:
      thread = threading.Thread(target=simulate_loop, name="failure_simulator")
      thread.start()
    else:
      simulate_loop()

    self.logger.info("Terminating failure simulator.")

  def induce_event(self, global_ranks: list[int]):
    """Simulates GPU failures by killing processes running on the failed GPUs.

    Args:
        global_ranks (list[int]): A list indicating the global ranks of which
          GPUs have failed.
    """
    if not global_ranks:
      return

    # Only induce events on GPUs within the current VM
    global_ranks = self.filter_global_ranks(global_ranks)
    local_ranks = self.global_to_local_ranks(global_ranks)

    self.logger.info(f"Filtered local ranks to affect: {local_ranks}")
    self._gpu_kill_fn(local_ranks)
