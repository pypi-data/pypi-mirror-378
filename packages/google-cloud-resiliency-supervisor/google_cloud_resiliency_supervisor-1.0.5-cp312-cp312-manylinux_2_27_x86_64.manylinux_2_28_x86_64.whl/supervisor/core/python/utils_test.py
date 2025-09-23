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

import sys

import pytest
from supervisor.core.python import utils


class TestUtils:
  """Tests for Google Cloud Resiliency Supervisor core utility functions."""

  @pytest.mark.parametrize(
      ("value", "expected_is_set"),
      (
          (None, False),
          (0, True),
          (-1, False),
          (1, True),
          (0.0, True),
          (1.0, True),
          ("hello", True),
      ),
  )
  def test_is_set(self, value, expected_is_set):
    assert utils.is_set(value) == expected_is_set

  @pytest.mark.parametrize(
      ("input_string_kwargs", "expected_kwargs", "should_raise_error"),
      (
          (None, {}, False),
          (
              "val1=hello,val2=2,val3=3.14,val4=-4",
              {"val1": "hello", "val2": 2, "val3": 3.14, "val4": -4},
              False,
          ),
          ("val1:hello", {}, True),
      ),
  )
  def test_destringify_kwargs(
      self, input_string_kwargs, expected_kwargs, should_raise_error
  ):
    """Tests the destringify_kwargs function."""
    if should_raise_error:
      with pytest.raises(ValueError):
        utils.destringify_kwargs(input_string_kwargs)

    else:
      kwargs = utils.destringify_kwargs(input_string_kwargs)
      assert kwargs == expected_kwargs


if __name__ == "__main__":
  sys.exit(pytest.main(sys.argv[1:]))
