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
from unittest import mock

import pytest
from supervisor.watchdogs.python import ecc_watchdog
import supervisor_core


@pytest.fixture
def watchdog():
  """Fixture to create an ECCWatchdog instance."""
  return ecc_watchdog.ECCWatchdog(error_threshold=2)


@mock.patch("subprocess.run")
def test_get_errors_no_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="00000000:01:00.0,0\n00000000:02:00.0,0\n",
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert errors == {
      "00000000:01:00.0": [{
          "xid_code": 48,
          "status": "healthy",
          "requires_notification": False,
      }],
      "00000000:02:00.0": [{
          "xid_code": 48,
          "status": "healthy",
          "requires_notification": False,
      }],
  }


@mock.patch("subprocess.run")
def test_get_errors_below_threshold(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="00000000:01:00.0,1\n00000000:02:00.0,1\n",
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert errors == {
      "00000000:01:00.0": [{
          "xid_code": 48,
          "status": "healthy",
          "requires_notification": False,
      }],
      "00000000:02:00.0": [{
          "xid_code": 48,
          "status": "healthy",
          "requires_notification": False,
      }],
  }


@mock.patch("subprocess.run")
def test_get_errors_at_threshold(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="00000000:01:00.0,2\n00000000:02:00.0,2\n",
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert errors == {
      "00000000:01:00.0": [{
          "xid_code": 48,
          "status": "error",
          "error_count": 2,
          "requires_notification": True,
      }],
      "00000000:02:00.0": [{
          "xid_code": 48,
          "status": "error",
          "error_count": 2,
          "requires_notification": True,
      }],
  }


@mock.patch("subprocess.run")
def test_get_errors_above_threshold(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="00000000:01:00.0,5\n00000000:02:00.0,10\n",
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert errors == {
      "00000000:01:00.0": [{
          "xid_code": 48,
          "status": "error",
          "error_count": 5,
          "requires_notification": True,
      }],
      "00000000:02:00.0": [{
          "xid_code": 48,
          "status": "error",
          "error_count": 10,
          "requires_notification": True,
      }],
  }


@mock.patch("subprocess.run")
def test_get_errors_above_threshold_no_notification(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  watchdog.last_gpu_error_counts = {"00000000:01:00.0": 5}
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="00000000:01:00.0,5\n",
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert errors == {
      "00000000:01:00.0": [{
          "xid_code": 48,
          "status": "error",
          "error_count": 5,
          "requires_notification": False,
      }],
  }


@mock.patch("subprocess.run")
def test_get_errors_invalid_output(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[], returncode=0, stdout="invalid_output"
  )
  with pytest.raises(ValueError):
    watchdog._get_errors()  # pylint: disable=protected-access


@mock.patch("subprocess.run")
def test_get_errors_command_failed(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.side_effect = subprocess.CalledProcessError(
      returncode=1, cmd="nvidia-smi", stderr="Command failed"
  )
  with pytest.raises(subprocess.CalledProcessError):
    watchdog._get_errors()  # pylint: disable=protected-access


def test_format_error_message(watchdog):
  error_data = {"error_count": 5}
  message = watchdog._format_error_message("00000000:01:00.0", error_data)  # pylint: disable=protected-access
  assert (
      message
      == "GPU 00000000:01:00.0: Detected 5 volatile double-bit ECC errors"
  )


@mock.patch("subprocess.run")
def test_poll_with_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout=(
          "pci_bus_id,ecc.errors.uncorrected.volatile.total\n"
          "00000000:01:00.0,5\n"
      ),
  )
  reports = watchdog.poll()
  assert len(reports) == 1
  assert reports[0].event_type == supervisor_core.EventType.ECC
  assert reports[0].device_id == "00000000:01:00.0"
  assert reports[0].xid_code == 48
  assert "5 volatile double-bit ECC errors" in reports[0].message


@mock.patch("subprocess.run")
def test_poll_no_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout=(
          "pci_bus_id,ecc.errors.uncorrected.volatile.total\n"
          "00000000:01:00.0,0\n"
      ),
  )
  reports = watchdog.poll()
  assert not reports


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
