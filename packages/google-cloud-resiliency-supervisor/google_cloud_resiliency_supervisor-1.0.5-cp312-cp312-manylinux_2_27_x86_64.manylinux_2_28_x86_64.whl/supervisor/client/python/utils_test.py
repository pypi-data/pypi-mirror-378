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
import sys
import time
from unittest import mock

from google.api_core import exceptions as api_exceptions
from google.cloud import compute_v1
import pytest
import requests
from supervisor.client.python import utils


class TestUtils:
  """Tests for Supervisor Python client utility functions."""

  @mock.patch.object(socket, "socket", autospec=True)
  def test_find_available_port(self, mock_socket):
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.getsockname.return_value = ["", 12345]
    port = utils.find_available_port()
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_socket_instance.bind.assert_called_once_with(("", 0))
    mock_socket_instance.getsockname.assert_called_once()
    mock_socket_instance.close.assert_called_once()
    assert port == 12345

  @mock.patch.object(socket, "socket", autospec=True)
  def test_find_available_port_bind_error(self, mock_socket):
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.bind.side_effect = socket.error(
        "Address already in use"
    )
    with pytest.raises(socket.error):
      utils.find_available_port()
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_socket_instance.bind.assert_called_once_with(("", 0))
    mock_socket_instance.close.assert_not_called()

  @mock.patch.object(socket, "socket", autospec=True)
  def test_find_available_port_getsockname_error(self, mock_socket):
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.getsockname.side_effect = socket.error(
        "An error occurred"
    )
    with pytest.raises(socket.error):
      utils.find_available_port()
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
    mock_socket_instance.bind.assert_called_once_with(("", 0))
    mock_socket_instance.getsockname.assert_called_once()
    mock_socket_instance.close.assert_not_called()

  @mock.patch.object(subprocess, "run", autospec=True)
  def test_launch_sync_proc_success(self, mock_run):
    mock_proc = mock.Mock()
    mock_proc.stdout = "Test output"
    mock_run.return_value = mock_proc
    command = ["echo", "hello"]
    output = utils.launch_sync_proc(command)
    mock_run.assert_called_once_with(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        text=True,
    )
    assert output == "Test output"

  @mock.patch.object(subprocess, "run", autospec=True)
  def test_launch_sync_proc_error(self, mock_run):
    mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")
    command = ["bad_command"]
    with pytest.raises(subprocess.CalledProcessError):
      utils.launch_sync_proc(command)
    mock_run.assert_called_once_with(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
        text=True,
    )

  @mock.patch.object(utils, "launch_sync_proc", autospec=True)
  def test_get_gpu_serial(self, mock_launch):
    mock_launch.return_value = "GPU-SERIAL-123\n"
    serial = utils.get_gpu_serial(local_rank=0)
    mock_launch.assert_called_once_with([
        "/usr/local/nvidia/bin/nvidia-smi",
        "--query-gpu",
        "serial",
        "--format",
        "csv,noheader",
        "-i",
        "0",
    ])
    assert serial == "GPU-SERIAL-123"

  @mock.patch.object(utils, "launch_sync_proc", autospec=True)
  def test_get_pci_bus_id_no_nsenter(self, mock_launch):
    mock_launch.return_value = "0000:81:00.0\n"
    bus_id = utils.get_pci_bus_id(local_rank=1, use_nsenter=False)
    mock_launch.assert_called_once_with([
        "/usr/local/nvidia/bin/nvidia-smi",
        "--query-gpu",
        "pci.bus_id",
        "--format",
        "csv,noheader",
        "-i",
        "1",
    ])
    assert bus_id == "0000:81:00.0"

  @mock.patch.object(utils, "launch_sync_proc", autospec=True)
  def test_get_pci_bus_id_with_nsenter(self, mock_launch):
    mock_launch.return_value = "0000:82:00.0\n"
    bus_id = utils.get_pci_bus_id(local_rank=2, use_nsenter=True)
    mock_launch.assert_called_once_with([
        "nsenter",
        "-at",
        "1",
        "--",
        "/home/kubernetes/bin/nvidia/bin/nvidia-smi",
        "--query-gpu=pci.bus_id",
        "--format=csv,noheader",
        "-i",
        "2",
    ])
    assert bus_id == "0000:82:00.0"

  @mock.patch.object(compute_v1, "InstancesClient", autospec=True)
  def test_get_host_physical_attributes_success(self, mock_client):
    mock_instance = mock.Mock()
    mock_instance.resource_status.physical_host = (
        "physicalHosts/sb1/rack2/serial3"
    )
    mock_client.return_value.get.return_value = mock_instance

    attrs = utils.get_host_physical_attributes("proj", "zone-a", "host1")

    mock_client.return_value.get.assert_called_once_with(
        project="proj",
        zone="zone-a",
        instance="host1",
        retry=mock.ANY,
    )
    assert attrs == ("sb1", "rack2", "serial3")

  @mock.patch.object(compute_v1, "InstancesClient", autospec=True)
  def test_get_host_physical_attributes_no_info(self, mock_client):
    mock_instance = mock.Mock()
    mock_instance.resource_status.physical_host = None
    mock_client.return_value.get.return_value = mock_instance

    attrs = utils.get_host_physical_attributes("proj", "zone-a", "host1")

    mock_client.return_value.get.assert_called_once_with(
        project="proj",
        zone="zone-a",
        instance="host1",
        retry=mock.ANY,
    )
    assert attrs == ("", "", "")

  @mock.patch.object(compute_v1, "InstancesClient", autospec=True)
  def test_get_host_physical_attributes_api_error(self, mock_client):
    mock_client.return_value.get.side_effect = api_exceptions.GoogleAPIError(
        "API Error"
    )

    with pytest.raises(api_exceptions.GoogleAPIError):
      utils.get_host_physical_attributes("proj", "zone-a", "host1")

    mock_client.return_value.get.assert_called_once_with(
        project="proj",
        zone="zone-a",
        instance="host1",
        retry=mock.ANY,
    )

  @mock.patch.object(requests, "get", autospec=True)
  def test_get_host_zone(self, mock_get):
    mock_response = mock.Mock()
    mock_response.text = "projects/12345/zones/us-central1-a"
    mock_get.return_value = mock_response

    zone = utils.get_host_zone()

    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/zone?alt=text",
        headers={"Metadata-Flavor": "Google"},
    )
    assert zone == "us-central1-a"

  @mock.patch.object(requests, "get", autospec=True)
  def test_get_host_zone_error(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network Error")
    with pytest.raises(requests.exceptions.RequestException):
      utils.get_host_zone()

  @mock.patch.object(socket, "socket", autospec=True)
  def test_get_host_ip(self, mock_socket):
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.getsockname.return_value = ("10.0.0.5", 54321)

    ip = utils.get_host_ip()

    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
    mock_socket_instance.connect.assert_called_once_with(("8.8.8.8", 80))
    mock_socket_instance.getsockname.assert_called_once()
    mock_socket_instance.close.assert_called_once()
    assert ip == "10.0.0.5"

  @mock.patch.object(socket, "socket", autospec=True)
  def test_get_host_ip_error(self, mock_socket):
    mock_socket_instance = mock_socket.return_value
    mock_socket_instance.connect.side_effect = socket.error("Connect Error")

    with pytest.raises(socket.error):
      utils.get_host_ip()

    mock_socket_instance.close.assert_called_once()

  @mock.patch.object(requests, "get", autospec=True)
  def test_get_host_id(self, mock_get):
    mock_response = mock.Mock()
    mock_response.text = "1234567890123456789"
    mock_get.return_value = mock_response

    host_id = utils.get_host_id()

    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/id?alt=text",
        headers={"Metadata-Flavor": "Google"},
    )
    assert host_id == "1234567890123456789"

  @mock.patch.object(requests, "get", autospec=True)
  def test_get_host_id_error(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network Error")
    with pytest.raises(requests.exceptions.RequestException):
      utils.get_host_id()

  @mock.patch.object(requests, "get", autospec=True)
  def test_get_host_name(self, mock_get):
    mock_response = mock.Mock()
    mock_response.text = "my-vm.c.my-project.internal"
    mock_get.return_value = mock_response

    host_name = utils.get_host_name()

    mock_get.assert_called_once_with(
        "http://metadata.google.internal/computeMetadata/v1/instance/hostname?alt=text",
        headers={"Metadata-Flavor": "Google"},
    )
    assert host_name == "my-vm"

  @mock.patch.object(requests, "get", autospec=True)
  def test_get_host_name_error(self, mock_get):
    mock_get.side_effect = requests.exceptions.RequestException("Network Error")
    with pytest.raises(requests.exceptions.RequestException):
      utils.get_host_name()

  @mock.patch.object(pathlib, "Path", autospec=True)
  @mock.patch.object(os, "remove", autospec=True)
  def test_clean_termination_files_exists(self, mock_remove, mock_path):
    mock_file = mock_path.return_value
    mock_file.exists.return_value = True
    mock_file.__str__.return_value = "/path/to/term/file"

    utils.clean_termination_files()

    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_file.exists.assert_called_once()
    mock_remove.assert_called_once_with(mock_file)

  @mock.patch.object(pathlib, "Path", autospec=True)
  @mock.patch.object(os, "remove", autospec=True)
  def test_clean_termination_files_not_exists(self, mock_remove, mock_path):
    mock_file = mock_path.return_value
    mock_file.exists.return_value = False

    utils.clean_termination_files()

    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_file.exists.assert_called_once()
    mock_remove.assert_not_called()

  @mock.patch.object(pathlib, "Path", autospec=True)
  @mock.patch.object(os, "remove", autospec=True)
  def test_clean_termination_files_os_error(self, mock_remove, mock_path):
    mock_file = mock_path.return_value
    mock_file.exists.return_value = True
    mock_remove.side_effect = OSError("Permission denied")

    utils.clean_termination_files()

    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_file.exists.assert_called_once()
    mock_remove.assert_called_once_with(mock_file)

  @mock.patch.object(pathlib, "Path", autospec=True)
  def test_check_termination_file_exists(self, mock_path):
    mock_file = mock_path.return_value
    mock_file.exists.return_value = True
    # self.assertTrue(utils.check_termination_file()) # Removed assertion
    assert utils.check_termination_file()  # Added assertion
    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_file.exists.assert_called_once()

  @mock.patch.object(pathlib, "Path", autospec=True)
  def test_check_termination_file_not_exists(self, mock_path):
    mock_file = mock_path.return_value
    mock_file.exists.return_value = False
    assert not utils.check_termination_file()
    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_file.exists.assert_called_once()

  @mock.patch.object(pathlib, "Path", autospec=True)
  @mock.patch.object(os, "makedirs", autospec=True)
  def test_create_termination_file(self, mock_makedirs, mock_path):
    mock_file = mock_path.return_value
    mock_parent = mock.Mock()
    mock_file.parent = mock_parent
    mock_file.__str__.return_value = "/path/to/term/file"

    utils.create_termination_file()

    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_makedirs.assert_called_once_with(mock_parent, exist_ok=True)
    mock_file.touch.assert_called_once()

  @mock.patch.object(pathlib, "Path", autospec=True)
  @mock.patch.object(os, "makedirs", autospec=True)
  def test_create_termination_file_os_error(self, mock_makedirs, mock_path):
    mock_file = mock_path.return_value
    mock_parent = mock.Mock()
    mock_file.parent = mock_parent
    mock_file.touch.side_effect = OSError("Cannot create")

    utils.create_termination_file()

    mock_path.assert_called_once_with(utils.TERM_FILE_BASE)
    mock_makedirs.assert_called_once_with(mock_parent, exist_ok=True)
    mock_file.touch.assert_called_once()

  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_free(self, mock_socket):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.return_value = 1

    assert utils.check_and_clean_port(8080)
    mock_socket_instance.connect_ex.assert_called_once_with(("localhost", 8080))

  @mock.patch.object(time, "sleep", autospec=True)
  @mock.patch.object(os, "kill", autospec=True)
  @mock.patch.object(subprocess, "run", autospec=True)
  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_in_use_sigterm_success(
      self, mock_socket, mock_run, mock_kill, mock_sleep
  ):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.side_effect = [0, 1]

    mock_proc = mock.Mock()
    mock_proc.stdout = "12345\n"
    mock_run.return_value = mock_proc

    assert utils.check_and_clean_port(8080, kill_delay=1)

    assert mock_socket_instance.connect_ex.call_count == 2
    mock_run.assert_called_once_with(
        ["lsof", "-t", "-i", "tcp:8080"],
        capture_output=True,
        text=True,
        check=True,
    )
    mock_kill.assert_called_once_with(12345, signal.SIGTERM)
    mock_sleep.assert_called_once_with(1)

  @mock.patch.object(time, "sleep", autospec=True)
  @mock.patch.object(os, "kill", autospec=True)
  @mock.patch.object(subprocess, "run", autospec=True)
  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_in_use_sigkill_success(
      self, mock_socket, mock_run, mock_kill, mock_sleep
  ):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.side_effect = [0, 0, 1]

    mock_proc = mock.Mock()
    mock_proc.stdout = "12345\n"
    mock_run.return_value = mock_proc

    assert utils.check_and_clean_port(8080, kill_delay=1)

    assert mock_socket_instance.connect_ex.call_count == 3
    mock_run.assert_called_once_with(
        ["lsof", "-t", "-i", "tcp:8080"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert mock_kill.call_count == 2
    mock_kill.assert_has_calls([
        mock.call(12345, signal.SIGTERM),
        mock.call(12345, signal.SIGKILL),
    ])
    assert mock_sleep.call_count == 2
    mock_sleep.assert_has_calls([mock.call(1), mock.call(1)])

  @mock.patch.object(time, "sleep", autospec=True)
  @mock.patch.object(os, "kill", autospec=True)
  @mock.patch.object(subprocess, "run", autospec=True)
  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_in_use_sigkill_fail(
      self, mock_socket, mock_run, mock_kill, mock_sleep
  ):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.return_value = 0

    mock_proc = mock.Mock()
    mock_proc.stdout = "12345\n"
    mock_run.return_value = mock_proc

    assert not utils.check_and_clean_port(8080, kill_delay=1)

    assert mock_socket_instance.connect_ex.call_count == 3
    mock_run.assert_called_once_with(
        ["lsof", "-t", "-i", "tcp:8080"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert mock_kill.call_count == 2
    mock_kill.assert_has_calls([
        mock.call(12345, signal.SIGTERM),
        mock.call(12345, signal.SIGKILL),
    ])
    assert mock_sleep.call_count == 2

  @mock.patch.object(subprocess, "run", autospec=True)
  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_lsof_error(self, mock_socket, mock_run):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.return_value = 0
    mock_run.side_effect = subprocess.CalledProcessError(1, "lsof")

    assert not utils.check_and_clean_port(8080)
    mock_run.assert_called_once()

  @mock.patch.object(subprocess, "run", autospec=True)
  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_lsof_no_pid(self, mock_socket, mock_run):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.return_value = 0

    mock_proc = mock.Mock()
    mock_proc.stdout = ""
    mock_run.return_value = mock_proc

    assert not utils.check_and_clean_port(8080)
    mock_run.assert_called_once()

  @mock.patch.object(os, "kill", autospec=True)
  @mock.patch.object(subprocess, "run", autospec=True)
  @mock.patch.object(socket, "socket", autospec=True)
  def test_check_and_clean_port_kill_error(
      self, mock_socket, mock_run, mock_kill
  ):
    mock_socket_instance = mock_socket.return_value.__enter__.return_value
    mock_socket_instance.connect_ex.return_value = 0

    mock_proc = mock.Mock()
    mock_proc.stdout = "12345\n"
    mock_run.return_value = mock_proc
    mock_kill.side_effect = OSError("No such process")

    assert not utils.check_and_clean_port(8080)
    mock_kill.assert_called_once_with(12345, signal.SIGTERM)

  @pytest.mark.parametrize(
      ("launch_output", "launch_side_effect", "expected_return"),
      [
          ("12345\n", None, True),  # Workload running
          ("", None, False),  # No workload
          (
              None,
              subprocess.CalledProcessError(1, "cmd"),
              False,
          ),  # Command error
      ],
  )
  @mock.patch.object(utils, "launch_sync_proc", autospec=True)
  def test_is_host_running_workload(
      self,
      mock_launch_sync_proc,
      launch_output,
      launch_side_effect,
      expected_return,
  ):
    """Tests the is_host_running_workload function."""
    mock_launch_sync_proc.return_value = launch_output
    mock_launch_sync_proc.side_effect = launch_side_effect

    assert utils.is_host_running_workload() is expected_return
    mock_launch_sync_proc.assert_called_once_with([
        "nsenter",
        "-at",
        "1",
        "--",
        "/home/kubernetes/bin/nvidia/bin/nvidia-smi",
        "--query-compute-apps=pid",
        "--format=csv,noheader",
    ])


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
