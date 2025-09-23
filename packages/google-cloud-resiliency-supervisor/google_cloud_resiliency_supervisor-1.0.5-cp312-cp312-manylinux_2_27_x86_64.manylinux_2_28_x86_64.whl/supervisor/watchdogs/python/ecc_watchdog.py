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

import collections
import subprocess
from typing import Any

from supervisor.watchdogs.python import base_watchdog
import supervisor_core


class ECCWatchdog(base_watchdog.BaseWatchdog):
  """Implementation of BaseWatchdog for ECC errors."""

  def __init__(
      self,
      sample_interval: int = 30,
      error_threshold: int = 1,
      notification_cooldown: int = 30,
  ):
    """Initialize ECC error Watchdog.

    Args:
        sample_interval: Time in seconds between error samples.
        error_threshold: Number of volatile double-bit errors to trigger alert.
        notification_cooldown: Time in seconds between notifications.
    """
    super().__init__(
        supervisor_core.EventType.ECC,
        error_threshold,
        sample_interval,
        notification_cooldown,
    )
    self.last_gpu_error_counts = collections.Counter()
    self.logger.info("Starting ECC watchdog.")

  def _get_errors(self) -> dict[str, list[dict[str, Any]]]:
    """Run nvidia-smi to get volatile double-bit ECC errors for all GPUs.

    Returns:
        Dict of PCI Bus ID to error data dictionary.
    """
    try:
      cmd = [
          "nsenter",
          "-at",
          "1",
          "--",
          "/home/kubernetes/bin/nvidia/bin/nvidia-smi",
          "--query-gpu=pci.bus_id,ecc.errors.uncorrected.volatile.total",
          "--format=csv,noheader",
      ]

      result = subprocess.run(cmd, capture_output=True, text=True, check=True)

      gpu_errors = collections.defaultdict(list)
      for line in result.stdout.strip().split("\n"):
        if line:
          pci_bus_id, errors_str = line.split(",")
          current_error_count = (
              int(errors_str) if errors_str.strip().isdigit() else 0
          )

          last_notified_error_count_for_gpu = self.last_gpu_error_counts[
              pci_bus_id
          ]

          status = {
              "xid_code": 48,
              "status": "healthy",
              "requires_notification": False,
          }

          if current_error_count >= self.error_threshold:
            status["status"] = "error"
            status["error_count"] = current_error_count

            if current_error_count != last_notified_error_count_for_gpu:
              status["requires_notification"] = True
              self.last_gpu_error_counts[pci_bus_id] = current_error_count

          else:
            status["status"] = "healthy"
            if last_notified_error_count_for_gpu >= self.error_threshold:
              self.last_gpu_error_counts[pci_bus_id] = current_error_count

          gpu_errors[pci_bus_id].append(status)

      if not gpu_errors:
        self.logger.debug("nvidia-smi found no ECC errors.")

      return gpu_errors

    except subprocess.CalledProcessError:
      self.logger.exception("nvidia-smi command failed.")
      raise
    except Exception:
      self.logger.exception("Error running nvidia-smi.")
      raise

  def _format_error_message(
      self, device_id: str, error_data: dict[str, Any]
  ) -> str:
    """Format the error message for logging and reporting.

    Args:
        device_id: String representation of GPU PCI Bus ID.
        error_data: Dictionary containing error information.

    Returns:
        Formatted error message.
    """
    return (
        f"GPU {device_id}: Detected {error_data['error_count']} volatile"
        " double-bit ECC errors"
    )
