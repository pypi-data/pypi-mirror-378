# Copyright 2025 hingebase

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""There is no public Python API, please use the CLI instead."""

__all__ = []

import importlib.metadata

import rattler.platform

__version__ = importlib.metadata.version("mahoraga")

if "emscripten-32" in rattler.platform.PlatformLiteral.__args__:
    rattler.platform.PlatformLiteral.__args__ = (  # pyright: ignore[reportAttributeAccessIssue]
        "noarch",
        "linux-32",
        "linux-64",
        "linux-aarch64",
        "linux-armv6l",
        "linux-armv7l",
        "linux-loong64",
        "linux-ppc64le",
        "linux-ppc64",
        "linux-ppc",
        "linux-s390x",
        "linux-riscv32",
        "linux-riscv64",
        "osx-64",
        "osx-arm64",
        "win-32",
        "win-64",
        "win-arm64",
        "emscripten-wasm32",
        "wasi-wasm32",
        "zos-z",
    )
