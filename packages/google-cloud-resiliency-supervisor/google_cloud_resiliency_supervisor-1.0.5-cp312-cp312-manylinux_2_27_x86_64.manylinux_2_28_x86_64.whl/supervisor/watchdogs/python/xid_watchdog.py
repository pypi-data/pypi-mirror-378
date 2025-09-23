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
import datetime
import re
import subprocess
from typing import Any

from supervisor.watchdogs.python import base_watchdog
import supervisor_core


class XIDWatchdog(base_watchdog.BaseWatchdog):
  """Implementation of BaseWatchdog for Xid errors."""

  def __init__(
      self,
      sample_interval: int = 30,
      error_threshold: int = 1,
      notification_cooldown: int = 30,
  ):
    """Initialize XID error Watchdog.

    Args:
        sample_interval: Time in seconds between error samples.
        error_threshold: Number of Xid errors to trigger alert.
    """
    super().__init__(
        supervisor_core.EventType.XID,
        error_threshold,
        sample_interval,
        notification_cooldown,
    )
    self.logger.info("Starting XID watchdog.")
    self.last_poll_time = datetime.datetime.now(tz=datetime.timezone.utc)

  def _parse_journalctl_output(
      self, journalctl_out: str
  ) -> dict[str, list[dict[str, Any]]]:
    """Parses the journalctl output for XID errors.

    Args:
        journalctl_out: The output of the journalctl command.

    Returns:
        A dictionary where keys are PCI bus IDs (str) and values are lists of
        error dictionaries.
    """
    xid_pattern = (
        r"NVRM: Xid"
        r" \(PCI:([0-9a-fA-F.:]+)\):\s*(\d+)(?:,\s*pid=.*?,\s*name=.*?)?,\s+(.*?)(?:\s*(?:,\s*)?(Ch\s+[0-9a-fA-F]+))?\s*\r?\n?$"
    )

    gpu_errors = collections.defaultdict(list)
    for line in journalctl_out.strip().splitlines():
      xid_match = re.search(xid_pattern, line)

      if xid_match:
        pci_bus_id = xid_match.group(1).strip()
        xid_code = xid_match.group(2).strip()
        message = xid_match.group(3)
        channel_info = xid_match.group(4)

        if channel_info:
          channel_info = channel_info.strip()

        if message:
          message = message.strip()

        # Adding leading and trailing zeros to match nvidia-smi
        if "00000000" not in pci_bus_id:
          pci_bus_id = "0000" + pci_bus_id

        if ".0" not in pci_bus_id:
          pci_bus_id = pci_bus_id + ".0"

        pci_bus_id = pci_bus_id.upper()

        status = {
            "xid_code": int(xid_code),
            "channel_info": channel_info,
            "message": message,
            "status": "error",
            "requires_notification": True,
        }
        gpu_errors[pci_bus_id].append(status)

    return gpu_errors

  def _merge_xid_errors(
      self, gpu_errors: dict[str, list[dict[str, Any]]]
  ) -> dict[str, list[dict[str, Any]]]:
    """Merges XID error entries for the same PCI bus ID and XID code.

    It iterates through the errors grouped by PCI bus ID. For each PCI ID,
    it further groups errors by XID code. If multiple errors share the same
    XID code, their 'message' and 'channel_info' fields are concatenated
    (separated by "; ") into a single error entry. Other fields like 'status'
    and 'requires_notification' are taken from the first error encountered
    in the group.

    Args:
      gpu_errors: A dictionary where keys are PCI bus IDs (str) and values are
        lists of error dictionaries.

    Returns:
      A dictionary with the same structure as the input, but with error
      entries merged where applicable.
    """
    # Create a new dictionary to store the merged results.
    merged_gpu_errors = {}

    # Iterate through each PCI bus ID and its list of errors
    for pci_bus_id, error_list in gpu_errors.items():
      if not error_list:
        merged_gpu_errors[pci_bus_id] = []  # Keep empty lists if they exist
        continue

      # Temporary dictionary to group errors by xid_code for *this* pci_bus_id
      errors_by_xid = collections.defaultdict(list)
      for status in error_list:
        xid_code = int(
            status.get("xid_code", -1)
        )  # Use -1 or handle error if key missing
        if xid_code != -1:
          errors_by_xid[xid_code].append(status)
        # else: handle or log error if xid_code is missing

      processed_errors_for_pci = []

      # Now iterate through the errors grouped by xid_code
      for xid_code, group in errors_by_xid.items():
        if len(group) == 1:
          # No merging needed if only one error has this xid_code
          processed_errors_for_pci.append(group[0])
        else:
          # Merge messages and channel info for this group

          # Use the first error entry as a base template
          merged_error = group[0].copy()

          # Collect non-empty messages and channel infos from the group
          messages_to_join = []
          channels_to_join = []

          for status in group:
            # Check for message existence and non-emptiness
            msg = status.get("message")
            if msg:
              messages_to_join.append(str(msg))  # Ensure string type

            # Check for channel_info existence and non-emptiness
            chan = status.get("channel_info")
            if chan:
              channels_to_join.append(str(chan))  # Ensure string type

          # Join collected strings with a separator "; "
          # Assign None if the resulting list was empty, otherwise join.
          merged_error["message"] = (
              "; ".join(messages_to_join) if messages_to_join else None
          )
          merged_error["channel_info"] = (
              "; ".join(channels_to_join) if channels_to_join else None
          )

          # Ensure the xid_code is correct (it's the key we grouped by)
          merged_error["xid_code"] = xid_code

          processed_errors_for_pci.append(merged_error)

      # Replace the original list with the processed list for this pci_bus_id
      merged_gpu_errors[pci_bus_id] = processed_errors_for_pci

    return merged_gpu_errors

  def _get_errors(self) -> dict[str, list[dict[str, Any]]]:
    """Run journalctl to get NVRM logs for XID errors on all GPUs.

    Returns:
        Dict of GPU PCI Bus ID to error information
    """

    # Get kernel logs via nsenter
    journalctl_cmd = [
        "nsenter",
        "-at",
        "1",
        "--",
        "journalctl",
        "-k",
        "--since",
        format(self.last_poll_time, "%Y-%m-%d %H:%M:%S UTC"),
    ]

    try:
      p1 = subprocess.run(
          journalctl_cmd, capture_output=True, text=True, check=True
      )
      journalctl_out = p1.stdout
      self.last_poll_time = datetime.datetime.now(tz=datetime.timezone.utc)

    except subprocess.CalledProcessError as e:
      self.logger.exception(
          f"Failed to run nsenter or journalctl with error: {e.returncode}"
      )
      raise

    gpu_errors = self._parse_journalctl_output(journalctl_out)
    gpu_errors = self._merge_xid_errors(gpu_errors)
    return gpu_errors

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
        f"GPU {device_id} Detected Xid error {error_data['xid_code']} with"
        f" channel info {error_data['channel_info']}: {error_data['message']}"
    )
