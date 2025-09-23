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

import argparse
#import distutils.dir_util
import os
import subprocess
import sys

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext


class BazelBuildExt(build_ext):

  def run(self):
    # 1. Get the path of the *current* Python interpreter
    python_path = sys.executable

    # 2. Get the version string (e.g., "3.12")
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"

    # 3. Set the environment variable for Bazel's build actions
    os.environ["PYTHON_BIN_PATH"] = python_path

    print(f"Building for Python {python_version} at: {python_path}")

    # Recommended: Clean Bazel to ensure no old 3.11 artifacts
    # subprocess.check_call(["bazel", "clean", "--expunge"])

    subprocess.check_call([
        "bazel",
        "build",
        "-c", "opt",

        # Explicitly tell Bazel what version to use
        f"--python_version=PY3",

        # Explicitly tell Bazel *where* to find that interpreter
        f"--python_path={python_path}",

        # Keep your original flag for the repository environment
        "--repo_env",
        f"PYTHON_BIN_PATH={python_path}",

        "//supervisor/core/cc:supervisor_core.so",
    ])

    # Ensure the build directory exists
    self.build_temp = self.build_temp or "build"
    #distutils.dir_util.mkpath(self.build_temp)
    from pathlib import Path
    Path(self.build_temp).mkdir(parents=True, exist_ok=True)

    # Copy the built library to the build directory
    built_lib_path = os.path.join(
        "bazel-bin", "supervisor", "core", "cc", "supervisor_core.so"
    )
    target_lib_path = self.get_ext_fullpath("supervisor_core")
    os.makedirs(os.path.dirname(target_lib_path), exist_ok=True)
    subprocess.check_call(["cp", built_lib_path, target_lib_path])


# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument(
    "--version",
    default="0.2.0",
    help="The version of the wheel to build",
)
parser.add_argument(
    "--python_version",
    default="3.10",
    help="The Python version to use for the build",
)
args, unknown = parser.parse_known_args()
sys.argv[1:] = unknown  # Pass unknown arguments back to setuptools

setup(
    name="google-cloud-resiliency-supervisor",
    version=args.version,
    author="Google Cloud",
    author_email="catmint-eng@google.com",
    description="Google Cloud Resiliency Supervisor",
    packages=find_packages(),
    ext_modules=[Extension("supervisor", sources=[])],
    cmdclass={"build_ext": BazelBuildExt},
    zip_safe=False,
    licenses=["Apache License 2.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
