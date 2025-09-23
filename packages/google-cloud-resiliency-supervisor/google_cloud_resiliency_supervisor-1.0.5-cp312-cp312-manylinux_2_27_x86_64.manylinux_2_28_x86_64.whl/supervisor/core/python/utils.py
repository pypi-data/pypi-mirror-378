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

import logging
import re
from typing import Any


def is_set(value: Any) -> bool:
  """Check if a value is set.

  Args:
      value: The value to check.

  Returns:
      bool: True if the value is set, False otherwise.
  """
  return value is not None and value != -1


def destringify_kwargs(string_kwargs: str | None) -> dict[str, Any]:
  """Convert kwargs in string format to usable dictionary.

  Args:
      string_kwargs: The string containing comma separated kwargs with format
        'KEY=VALUE'.

  Returns:
      dict: The dictionary representation of the kwargs.

  Raises:
      ValueError: If the string contains a colon, which is not supported.
  """

  def is_digit(string):
    return bool(re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", string))

  result = {}
  if string_kwargs is None or not string_kwargs:
    return result

  if ":" in string_kwargs:
    raise ValueError(
        "String kwargs contains a colon, which is not supported: %s. Please use"
        " equals '=' instead." % string_kwargs
    )

  kwargs = string_kwargs.split(",")
  for kwarg in kwargs:
    key, value = kwarg.split("=")
    if is_digit(value):
      try:
        value = int(value)
      except ValueError:
        value = float(value)
    result[key] = value

  return result


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
