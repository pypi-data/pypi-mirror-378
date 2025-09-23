# Copyright 2021 - 2025 Universität Tübingen, DKFZ, EMBL, and Universität zu Köln
# for the German Human Genome-Phenome Archive (GHGA)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utilities for generating temporary files."""

from __future__ import annotations

import sys
from abc import ABC
from collections.abc import Generator
from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from typing import BinaryIO, cast

__all__ = ["NamedBinaryIO", "big_temp_file"]


class NamedBinaryIO(ABC, BinaryIO):
    """Return type of NamedTemporaryFile."""

    name: str


@contextmanager
def big_temp_file(size: int) -> Generator[NamedBinaryIO, None, None]:
    """Generate a big file with approximately the specified size in bytes."""
    max_size = 2**31 - 1
    original_max = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(max_size)

    current_size = 0
    current_number = 0
    next_number = 1
    with NamedTemporaryFile("w+b") as temp_file:
        while current_size <= size:
            byte_addition = f"{current_number}\n".encode("ASCII")
            current_size += len(byte_addition)
            temp_file.write(byte_addition)
            previous_number = current_number
            current_number = next_number
            next_number = previous_number + current_number

        temp_file.flush()
        sys.set_int_max_str_digits(original_max)
        yield cast(NamedBinaryIO, temp_file)
