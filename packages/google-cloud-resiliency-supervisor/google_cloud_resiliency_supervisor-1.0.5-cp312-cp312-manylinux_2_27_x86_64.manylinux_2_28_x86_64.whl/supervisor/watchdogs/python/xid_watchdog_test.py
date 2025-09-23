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
from supervisor.watchdogs.python import xid_watchdog
import supervisor_core


@pytest.fixture
def watchdog():
  """Fixture to create an XIDWatchdog instance."""
  return xid_watchdog.XIDWatchdog()


@mock.patch("subprocess.run")
def test_get_errors_no_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[], returncode=0, stdout=""
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert not errors


@mock.patch("subprocess.run")
def test_get_errors_with_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout=(
          "NVRM: Xid (PCI:0000:86:00): 63, pid='<unknown>', name='<unknown>',"
          " Row Remapper: new row (ffff88803490344) marked for reaping: reset"
          " gpu to activate.\r\n"
          "NVRM: Xid (PCI:0000:86:00): 94, pid='<unknown>', name='<unknown>',"
          " Contained: SM (0x1). (pid 0), RST: No, D-RSTL No\r\n"
          "NVRM: Xid (PCI:0000:86:00): 94, pid='<unknown>', name='<unknown>',"
          " Ch 00000009\r\n"
          "2025-01-14 10:00:00.000 gke-node-gpu-abc [12345] NVRM: Xid"
          " (PCI:0000:01:00): 79, pid='5432', name='my_process', Graphics"
          " Engine Error, Ch 0000001A\r\n"
          "2025-01-14 11:00:00.000 gke-node-gpu-xyz [5678] NVRM: Xid"
          " (PCI:0000:02:00): 31, pid='9876', name='another_app', FIFO Error"
      ),
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert errors == {
      "00000000:86:00.0": [
          {
              "xid_code": 63,
              "status": "error",
              "requires_notification": True,
              "channel_info": None,
              "message": (
                  "Row Remapper: new row (ffff88803490344) marked for"
                  " reaping: reset gpu to activate."
              ),
          },
          {
              "xid_code": 94,
              "status": "error",
              "requires_notification": True,
              "channel_info": "Ch 00000009",
              "message": "Contained: SM (0x1). (pid 0), RST: No, D-RSTL No",
          },
      ],
      "00000000:01:00.0": [{
          "xid_code": 79,
          "status": "error",
          "requires_notification": True,
          "channel_info": "Ch 0000001A",
          "message": "Graphics Engine Error",
      }],
      "00000000:02:00.0": [{
          "xid_code": 31,
          "status": "error",
          "requires_notification": True,
          "channel_info": None,
          "message": "FIFO Error",
      }],
  }


@mock.patch("subprocess.run")
def test_get_errors_invalid_output(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[], returncode=0, stdout="invalid_output"
  )
  errors = watchdog._get_errors()  # pylint: disable=protected-access
  assert not errors


@mock.patch("subprocess.run")
def test_get_errors_command_failed(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.side_effect = subprocess.CalledProcessError(
      returncode=1, cmd="journalctl", stderr="Command failed"
  )
  with pytest.raises(subprocess.CalledProcessError):
    watchdog._get_errors()  # pylint: disable=protected-access


def test_format_error_message(watchdog):  # pylint: disable=redefined-outer-name
  error_data = {
      "xid_code": 53,
      "status": "error",
      "requires_notification": True,
      "message": "Fatal, Link 00 TSID Error",
      "channel_info": "Ch 00000000",
  }
  message = watchdog._format_error_message("0000:00:00.0", error_data)  # pylint: disable=protected-access
  assert (
      message
      == "GPU 0000:00:00.0 Detected Xid error 53 with channel info Ch"
      " 00000000: Fatal, Link 00 TSID Error"
  )


@mock.patch("subprocess.run")
def test_poll_with_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[],
      returncode=0,
      stdout="NVRM: Xid (PCI:0000:00:00.0): 53, Fatal, Link 00 TSID Error\n",
  )
  reports = watchdog.poll()
  assert len(reports) == 1
  assert reports[0].event_type == supervisor_core.EventType.XID
  assert reports[0].device_id == "00000000:00:00.0"
  assert reports[0].xid_code == 53
  assert "Detected Xid error 53" in reports[0].message


@mock.patch("subprocess.run")
def test_poll_no_errors(mock_run, watchdog):  # pylint: disable=redefined-outer-name
  mock_run.return_value = subprocess.CompletedProcess(
      args=[], returncode=0, stdout=""
  )
  reports = watchdog.poll()
  assert not reports


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
