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
import subprocess
import threading
import time
import numpy as np
from numpy import typing
from simulator.python import base_simulator


class GPUSlowdownSimulator(base_simulator.BaseSimulator):
  """Simulates GPU slowdowns in a distributed training environment.

  This class simulates GPU slowdowns by imposing a power limit on individual
  GPUs based on a given Mean Time Between Failures (MTBF). It uses a Poisson
  distribution to model the slowdown probability.
  """

  def __init__(
      self,
      rank: int,
      gpu_world_size: int,
      gpus_per_node: int = 8,
      seed: int = 42,
  ):
    """Initializes instance of GPUSlowdownSimulator.

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
    self.logger.info("Initializing GPU slowdown simulator.")
    self._slow_gpus = {}
    self._repair_slow_gpus_thread = None

  def _repair_slow_gpus(self, check_interval: int = 5):
    """Monitors _slow_gpus and resets GPUs when slowdown duration expires.

    Args:
        check_interval (int): The interval in seconds between checks. Defaults
          to 5s.
    """
    self.logger.info("Starting GPU slowdown repair thread.")

    while not self.is_completed():
      time.sleep(check_interval)
      current_time = time.monotonic()

      for local_rank, (duration, start_time) in list(self._slow_gpus.items()):
        if current_time - start_time >= duration:
          self.logger.info(
              f"Slowdown expired for GPU local rank: {local_rank}. Resetting."
          )
          self._gpu_reset_fn([local_rank])

    self.logger.info("GPU slowdown monitor thread terminating.")

  def _gpu_slowdown_fn(
      self,
      local_ranks: list[int],
      duration: int = 300,
      gpu_power_limit: int = 200,
  ):
    """Slows down the GPUs on specified local ranks.

    Args:
        local_ranks (list[int]): The ranks of GPUs to be slowed.
        duration (int): The duration of the slowdown in seconds. Defaults to
          300s.
        gpu_power_limit (int): The power limit to be imposed on the GPUs.
          Defaults to 200W.
    """
    self.logger.info(f"Slowing down GPUs with local ranks: {local_ranks}.")
    local_ranks_str = ",".join([str(rank) for rank in local_ranks])
    slow_gpu_cmd = f"nvidia-smi -pl {gpu_power_limit} -i {local_ranks_str}"

    try:
      subprocess.run(
          slow_gpu_cmd.split(),
          capture_output=True,
          check=True,
          shell=False,
          text=True,
      )
      self.logger.info(f"Command {slow_gpu_cmd} succeeded.")

      for rank in local_ranks:
        self._slow_gpus[rank] = (duration, time.monotonic())

    except subprocess.CalledProcessError as e:
      self.logger.warning(f"Command {slow_gpu_cmd} failed with {e}.")

  def _gpu_reset_fn(self, local_ranks: list[int] | None = None):
    """Removes the slowdowns from the GPUs on specified local ranks.

    Args:
        local_ranks (list[int]): The ranks of GPUs to be slowed.
    """

    self.logger.info(
        f"Resetting GPU slowdowns on GPUs with local ranks: {local_ranks}."
    )

    if local_ranks is not None:
      reset_gpu_cmd = (
          "nvidia-smi -pl 700 -i"
          f" {','.join([str(rank) for rank in local_ranks])}"
      )
    else:
      reset_gpu_cmd = "nvidia-smi -pl 700"

    try:
      subprocess.run(
          reset_gpu_cmd.split(),
          capture_output=True,
          check=True,
          shell=False,
          text=True,
      )
      self.logger.info(f"Command {reset_gpu_cmd} succeeded.")

      if local_ranks is not None:
        for rank in local_ranks:
          if rank in self._slow_gpus:
            self._slow_gpus.pop(rank)
      else:
        self._slow_gpus.clear()

    except subprocess.CalledProcessError as e:
      self.logger.warning(f"Command {reset_gpu_cmd} failed with {e.stderr}.")

  def sample(self, lambda_value: float) -> typing.NDArray[bool]:
    """Samples for GPU slowdowns based on the Poisson distribution.

    Args:
        lambda_value (float): The lambda value of the Poisson distribution.

    Returns:
        NDArray[bool]: A boolean array indicating which GPUs have failed.
    """
    random_numbers = np.random.rand(self.gpus_per_node)
    probabilities = self.distribution(lambda_value, self.gpus_per_node)
    return random_numbers < probabilities

  def simulate(
      self,
      mtbf: float,
      sample_interval: int,
      duration: int = 300,
      gpu_power_limit: int = 200,
      run_async: bool = False,
      mutex: type(threading.Lock()) | None = None,
  ):
    """Starts the slowdown simulation loop.

    This method continuously samples for slowdowns and simulates them by
    limiting the power of the corresponding GPUs. It runs until a
    termination file is detected.

    Args:
        mtbf (float): The Mean Time Between Failures (MTBF) in years.
        sample_interval (int): The interval in seconds between samples.
        duration (int): The duration of the slowdown in seconds. Defaults to
          300s.
        gpu_power_limit (int): The power limit to be imposed on the GPUs.
          Defaults to 200W.
        run_async (bool): Whether to run the simulation asynchronously. Defaults
          to False.
        mutex (LockType): Optional mutex to synchronize multiple simulatenous
          simulators. Defaults to None.

    Raises:
        ValueError: If the GPU power limit is not between 200W and 700W.
    """
    mtbf_s = mtbf * 365 * 24 * 3600
    lambda_value = (1 / mtbf_s) * sample_interval
    mutex = mutex if mutex is not None else contextlib.nullcontext()

    if gpu_power_limit > 700 or gpu_power_limit < 200:
      raise ValueError("GPU power limit must be between 200W and 700W.")

    self.logger.info(
        f"Starting simulation loop with MTBF: {mtbf} years and sample interval:"
        f" {sample_interval} seconds."
    )

    def simulate_loop():
      while not self.is_completed():
        slowdown_events = self.sample(lambda_value)
        if slowdown_events.any():
          with mutex:
            slowdown_ranks = np.where(slowdown_events)[0].tolist()
            global_ranks = self.local_to_global_ranks(slowdown_ranks)
            self.induce_event(
                global_ranks,
                duration=duration,
                gpu_power_limit=gpu_power_limit,
            )

        time.sleep(sample_interval)
        current_time = time.monotonic()
        for local_rank, (slowdown_duration, start_time) in list(
            self._slow_gpus.items()
        ):
          if current_time - start_time >= slowdown_duration:
            self.logger.info(
                f"Slowdown expired for GPU local rank: {local_rank}. Resetting."
            )
            self._gpu_reset_fn([local_rank])

    if run_async:
      thread = threading.Thread(target=simulate_loop, name="slowdown_simulator")
      thread.start()
    else:
      simulate_loop()

    self.logger.info("Terminating slowdown simulator.")
    self._gpu_reset_fn()

  def induce_event(
      self,
      global_ranks: list[int],
      duration: int = 300,
      gpu_power_limit: int = 200,
  ):
    """Simulates GPU slowdowns by killing processes running on the failed GPUs.

    Args:
        global_ranks (list[int]): A list indicating the global ranks of which
          GPUs have failed.
        duration (int): The duration of the slowdown in seconds. Defaults to
          300s.
        gpu_power_limit (int): The power limit to be imposed on the GPUs.
          Defaults to 200W.

    Raises:
        ValueError: If the GPU power limit is not between 200W and 700W.
    """
    if not global_ranks:
      return

    if gpu_power_limit > 700 or gpu_power_limit < 200:
      raise ValueError("GPU power limit must be between 200W and 700W.")

    self.logger.info(
        f"Simulating slowdowns on GPUs: {global_ranks} with power:"
        f" {gpu_power_limit}W."
    )

    if self._repair_slow_gpus_thread is None:
      self._repair_slow_gpus_thread = threading.Thread(
          target=self._repair_slow_gpus, name="repair_slow_gpus", daemon=True
      )
      self._repair_slow_gpus_thread.start()

    # Only induce events on GPUs within the current VM
    filtered_global_ranks = self.filter_global_ranks(global_ranks)
    local_ranks = self.global_to_local_ranks(filtered_global_ranks)

    self.logger.info(f"Filtered local ranks to affect: {local_ranks}")

    filtered_local_ranks = []
    for rank in local_ranks:
      if rank not in self._slow_gpus:
        filtered_local_ranks.append(rank)
      else:
        self.logger.info(f"GPU local rank {rank} already has a slowdown.")

    if not filtered_local_ranks:
      self.logger.info("No GPUs to slow down.")
      return

    self._gpu_slowdown_fn(filtered_local_ranks, duration, gpu_power_limit)
    self.logger.info(f"Slow GPUs: {self._slow_gpus}")
