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
import pathlib
import signal
import socket
import subprocess
import time

from absl import logging
from google.api_core import exceptions
from google.api_core import retry
from google.cloud import compute_v1
import requests


TERM_FILE_BASE = "/usr/share/supervisor/workload_terminated"

_default_retry_policy = retry.Retry(
    predicate=retry.if_exception_type(exceptions.GoogleAPIError),
    initial=1.0,
    maximum=10.0,
    multiplier=1.3,
    deadline=15.0,
)


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


def find_available_port() -> int:
  """Find an available port."""
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  sock.bind(("", 0))
  port = sock.getsockname()[1]
  sock.close()
  return port


def get_gpu_serial(local_rank: int) -> str:
  """Gets the serial number of the GPU for the given rank via nvidia-smi.

  Args:
    local_rank: Workload rank within the node

  Returns:
    The GPU serial number as a string
  """
  return launch_sync_proc([
      "/usr/local/nvidia/bin/nvidia-smi",
      "--query-gpu",
      "serial",
      "--format",
      "csv,noheader",
      "-i",
      str(local_rank),
  ]).strip()


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


def get_host_physical_attributes(
    project_id: str, zone: str, host_name: str
) -> tuple[str, str, str]:
  """Gets the physical attributes of this host.

  Args:
    project_id: The project ID of the host.
    zone: The zone of the host.
    host_name: The name of the host.

  Returns:
    Tuple containing Superblock, Subblock (Rack) and Serial Number

  Raises:
    GoogleAPIError: If the Google API call fails after retries.
  """
  try:
    instance_client = compute_v1.InstancesClient()
    instance = instance_client.get(
        project=project_id,
        zone=zone,
        instance=host_name,
        retry=_default_retry_policy,
    )
    if instance and instance.resource_status.physical_host:
      superblock_id, subblock_id, host_serial_number = (
          instance.resource_status.physical_host.split("/")[1:]
      )
      return superblock_id, subblock_id, host_serial_number
    else:
      logging.info(
          "No information was available to parse. Is this machine in a compact"
          " placement group?"
      )
      return "", "", ""
  except exceptions.GoogleAPIError as e:
    logging.exception("Error getting host attributes after retries: %s", e)
    raise


def get_host_zone() -> str:
  """Gets the zone of this host.

  Returns:
    String representing the zone of this host.
  """
  try:
    return requests.get(
        "http://metadata.google.internal/computeMetadata/v1/instance/zone?alt=text",
        headers={"Metadata-Flavor": "Google"},
    ).text.split("/")[-1]
  except RuntimeError as e:
    logging.exception("Zone query to Google Cloud metadata server failed.")
    raise e


def get_host_ip() -> str:
  """Gets the IP address of the host machine.

  Returns:
    The IP address of the host machine as a string.
  """
  s = None
  try:
    # Create a socket object
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Connect to a remote host (doesn't actually need to be reachable)
    s.connect(("8.8.8.8", 80))
    # Get the local IP address assigned to the socket
    ip_address, _ = s.getsockname()
    return ip_address
  except Exception as e:
    logging.exception("Error getting host IP address.")
    raise e
  finally:
    if s is not None:
      s.close()


def get_host_id() -> str:
  """Gets the ID of this VM.

  Returns:
    The VM ID of this VM
  """
  try:
    return requests.get(
        "http://metadata.google.internal/computeMetadata/v1/instance/id?alt=text",
        headers={"Metadata-Flavor": "Google"},
    ).text
  except RuntimeError as e:
    logging.exception("VM ID query to Google Cloud metadata server failed.")
    raise e


def get_host_name() -> str:
  """Gets the Name of this VM.

  Host name is returned in format of
  <VM_Name>.<Zone>.<Sub-zone>.<Project>.<Project-Tenant>

  Returns:
    The VM Name of this VM.
  """
  try:
    full_name = requests.get(
        "http://metadata.google.internal/computeMetadata/v1/instance/hostname?alt=text",
        headers={"Metadata-Flavor": "Google"},
    ).text

    host_name = full_name.split(".")[0]
    logging.info(
        "Got host name: %s from full response %s", host_name, full_name
    )
    return host_name
  except RuntimeError as e:
    logging.exception(
        "VM hostname query to Google Cloud metadata server failed."
    )
    raise e


def is_host_running_workload() -> bool:
  """Checks for running processes on any GPU to determine if a workload is active.

  This is done by querying for running compute applications using nvidia-smi.

  Returns:
    True if there are any compute processes running on any GPU, False otherwise.
  """
  try:
    output = launch_sync_proc([
        "nsenter",
        "-at",
        "1",
        "--",
        "/home/kubernetes/bin/nvidia/bin/nvidia-smi",
        "--query-compute-apps=pid",
        "--format=csv,noheader",
    ])
    # If nvidia-smi returns any process IDs, a workload is running.
    return bool(output.strip())
  except subprocess.CalledProcessError as e:
    logging.info(
        "nvidia-smi command failed, assuming no workload is running: %s", e
    )
    return False


def clean_termination_files():
  """Cleans up old termination files."""
  try:
    file = _get_term_filepath()
    if file.exists():
      os.remove(file)
      logging.info("Removed old termination file %s", file)
  except OSError:
    logging.warning("Failed to remove old termination files.")


def _get_term_filepath() -> pathlib.Path:
  """Returns the termination semaphore file path.

  Returns:
      Termination semaphore file path
  """
  return pathlib.Path(f"{TERM_FILE_BASE}")


def check_termination_file() -> bool:
  """Returns whether the termination file exists or not."""
  file = _get_term_filepath()
  return file.exists()


def create_termination_file():
  """Creates workload termination semaphores shared with other containers."""
  try:
    logging.info("Creating termination file")
    f = _get_term_filepath()
    os.makedirs(f.parent, exist_ok=True)
    f.touch()
    logging.info("Created termination file at %s", f)
  except OSError:
    logging.warning("Failed to create termination file.")


def check_and_clean_port(port: int, kill_delay: int = 5) -> bool:
  """Checks if a given port is in use.

  If so, attempts to identify and terminate the process using the port, then
  rechecks.

  Args:
      port: The port number (integer) to check.
      kill_delay: Time (in seconds) to wait after sending SIGTERM before sending
        SIGKILL.

  Returns:
      True if the port is now free, False if the port is still in use
      after attempting to clean it, or if an error occurred.
  """

  def is_port_in_use(port: int):
    """Helper function to check if a port is currently in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      return s.connect_ex(("localhost", port)) == 0

  if not is_port_in_use(port):
    logging.info("Port %i is free.", port)
    return True

  logging.info("Port %i is in use. Attempting to clean...", port)

  try:
    # Use lsof to find the PID using the port.  More reliable than fuser
    # -n tcp: Only look at TCP ports.
    # -t: Output only the PID (terse mode).
    # -i: Specify the port to check
    result = subprocess.run(
        ["lsof", "-t", "-i", f"tcp:{port}"],
        capture_output=True,
        text=True,
        check=True,
    )
    pid_str = result.stdout.strip()

    if not pid_str:
      logging.info(
          "Could not find a process using port %d (lsof returned empty output)."
      )
      return (
          False  # Port is *claimed* to be in use, but we couldn't find the PID
      )

    pid = int(pid_str)
    logging.info("Process ID %i is using port %i.", pid, port)

    # Try to gracefully terminate the process (SIGTERM).
    logging.info("Sending SIGTERM to process %i...", pid)
    os.kill(pid, signal.SIGTERM)
    time.sleep(kill_delay)  # Give the process time to exit

    if not is_port_in_use(port):
      logging.info("Port %i is now free (process terminated gracefully).", port)
      return True

    # If still in use, forcefully terminate (SIGKILL).
    logging.info(
        "Process %i did not terminate gracefully. Sending SIGKILL...", pid
    )
    os.kill(pid, signal.SIGKILL)
    time.sleep(1)  # Short delay to allow OS to clean up

    if not is_port_in_use(port):
      logging.info("Port %i is now free (process killed).", port)
      return True
    else:
      logging.info(
          "Port %i is still in use after SIGKILL.  Manual intervention may"
          " be required.",
          port,
      )
      return False

  except subprocess.CalledProcessError:
    logging.exception("Error running lsof.")
    return False
  except ValueError:
    logging.exception("lsof returned invalid PID.")
    return False
  except OSError:
    logging.exception("Error killing process.")
    return False
  except RuntimeError:
    logging.exception("An unexpected error.")
    return False
