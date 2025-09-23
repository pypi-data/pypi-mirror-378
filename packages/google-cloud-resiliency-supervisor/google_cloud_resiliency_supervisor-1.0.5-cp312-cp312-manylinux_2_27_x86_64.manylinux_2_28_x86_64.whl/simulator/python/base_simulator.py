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

import abc
import logging
import pathlib
import subprocess
import numpy as np
from numpy import typing

TERM_FILE_BASE = "/usr/share/supervisor/workload_terminated"


def setup_logger() -> logging.Logger:
  """Sets up the logger with a specific prefix format.

  Returns:
      logging.Logger: The logger object.
  """
  logger = logging.getLogger(__name__)
  logger.setLevel(logging.INFO)

  # Check if a handler already exists
  if not logger.handlers:
    formatter = logging.Formatter(
        "%(levelname)s %(asctime)s  %(process)d %(filename)s:%(lineno)d]"
        " %(message)s"
    )
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

  logger.propagate = False
  return logger


def check_termination_file() -> bool:
  """Returns whether the termination file exists or not."""
  file = _get_term_filepath()
  return file.exists()


def _get_term_filepath() -> pathlib.Path:
  """Returns the termination semaphore file path.

  Returns:
      Termination semaphore file path
  """
  return pathlib.Path(f"{TERM_FILE_BASE}")


def launch_sync_proc(command: list[str]) -> str:
  """Launches a process, waits for it to finish, and returns its output.

  Args:
    command: Command to execute, split into spaceless strings

  Returns:
    The output of the subprocess, including both stderr and stdout
  """
  logging.info("Executing: %s", command)
  proc = subprocess.run(
      command,
      check=True,
      stdout=subprocess.PIPE,
      stderr=subprocess.STDOUT,
      encoding="utf-8",
      text=True,
  )
  output = proc.stdout
  logging.info("Output: %s", output)
  return output


def get_pci_bus_id(local_rank: int, use_nsenter: bool = False) -> str:
  """Gets the PCI Bus ID of the GPU for the given rank via nvidia-smi.

  Args:
    local_rank: Workload rank within the node
    use_nsenter: Whether to use nsenter to run nvidia-smi

  Returns:
    The GPU serial number as a string
  """
  if use_nsenter:
    cmd = [
        "nsenter",
        "-at",
        "1",
        "--",
        "/home/kubernetes/bin/nvidia/bin/nvidia-smi",
        "--query-gpu=pci.bus_id",
        "--format=csv,noheader",
        "-i",
        str(local_rank),
    ]
  else:
    cmd = [
        "/usr/local/nvidia/bin/nvidia-smi",
        "--query-gpu",
        "pci.bus_id",
        "--format",
        "csv,noheader",
        "-i",
        str(local_rank),
    ]

  return launch_sync_proc(cmd).strip()


class BaseSimulator(abc.ABC):
  """An abstract base class for defining failure simulators used for goodput studies.

  This class provides a common interface for different types of failure
  simulators. Concrete simulators should inherit from this class and implement
  the abstract methods.
  """

  def __init__(
      self,
      rank: int,
      gpu_world_size: int,
      gpus_per_node: int = 8,
      seed: int = 42,
  ):
    """Initializes the BaseSimulator with common parameters.

    Args:
        rank (int): The rank of the VM running the simulator.
        gpu_world_size (int): The total number of GPUs in the distributed
          environment.
        gpus_per_node (int, optional): The number of GPUs per node. Defaults to
          8.
        seed (int, optional): The seed for the random number generator. Defaults
          to 42.
    """
    self.rank = rank
    self.gpu_world_size = gpu_world_size
    self.gpus_per_node = gpus_per_node
    self.seed = seed

    self._rng = np.random.default_rng(seed=self.seed)

  def local_to_global_ranks(self, local_ranks: list[int]) -> list[int]:
    """Converts local ranks to global ranks.

    Args:
        local_ranks (list[int]): A list of local ranks.

    Returns:
        list[int]: A list of global ranks corresponding to the input local
        ranks.
    """
    global_ranks = [
        rank + (self.rank * self.gpus_per_node) for rank in local_ranks
    ]
    return global_ranks

  def global_to_local_ranks(self, global_ranks: list[int]) -> list[int]:
    """Converts local ranks to global ranks.

    Args:
        global_ranks (list[int]): A list of global ranks.

    Returns:
        list[int]: A list of global ranks corresponding to the input local
        ranks.
    """
    local_ranks = [rank % self.gpus_per_node for rank in global_ranks]
    return local_ranks

  def filter_global_ranks(self, global_ranks: list[int]) -> list[int]:
    """Filters out GPUs with global rank outside of the current VM's range.

    Args:
        global_ranks (list[int]): A list of global ranks.

    Returns:
        list[int]: A list of global ranks corresponding to the current VM.
    """
    filtered_global_ranks = [
        rank
        for rank in global_ranks
        if rank >= (self.rank * self.gpus_per_node)
        and rank < ((self.rank + 1) * self.gpus_per_node)
    ]
    return filtered_global_ranks

  def distribution(self, lambda_value: float, size: int) -> typing.NDArray[int]:
    """Queries the probability distribution used for sampling failures.

    Args:
        lambda_value (float): The lambda value used to calculate the
          distribution.
        size (int): The size of the distribution.

    Returns:
        Callable: The numpy Generator distribution used for sampling failures.
    """
    return self._rng.poisson(lambda_value, size)

  def is_completed(self) -> bool:
    """Checks if the simulation is completed."""
    return check_termination_file()

  @abc.abstractmethod
  def sample(self, *args, **kwargs) -> typing.NDArray[bool]:
    """Samples for a failure event across all GPUs.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.

    Returns:
        np.ndarray[bool]: A boolean array indicating which GPUs have failed.
    """

  @abc.abstractmethod
  def simulate(
      self,
      *args,
      **kwargs,
  ):
    """Starts the failure simulation.

    This method defines the main loop for the simulation and should be
    implemented by concrete simulators to define the specific failure simulation
    logic.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.
    """

  @abc.abstractmethod
  def induce_event(self, *args, **kwargs):
    """Induces failure event determinisitcally.

    This method defines a mechanism to manually induce a failure event and
    should be implemented by concrete simulators to define the specific failure
    event logic.

    Args:
        *args: Positional arguments.
        **kwargs: Keyword arguments.
    """
