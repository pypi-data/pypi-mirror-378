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
#

"""Functionality for testing FastAPI-based APIs."""

import socket
from collections.abc import Callable
from typing import Any, Generic, TypeVar

import httpx

__all__ = ["AsyncTestClient", "get_free_port"]


def get_free_port() -> int:
    """Find and return a free port on localhost."""
    sock = socket.socket()
    sock.bind(("", 0))
    return int(sock.getsockname()[1])


TApp = TypeVar("TApp", bound=Callable[..., Any])


class AsyncTestClient(httpx.AsyncClient, Generic[TApp]):
    """Client for testing ASGI apps in the context of a running async event loop.

    Usage: ```
    from fastapi import FastAPI
    from ghga_service_commons.api.testing import AsyncTestClient

    app = FastAPI()

    @app.get("/")
    def index():
        return "Hello World"

    @pytest.mark.asyncio
    async def test_index():
        async with AsyncTestClient(app) as client:
            response = await client.get("/")

    assert response.status_code == 200
    assert response.json() == "Hello World"
    ```
    """

    app: TApp

    def __init__(self, app: TApp):
        """Initialize with ASGI app."""
        self.app = app  # make the application available to tests as well
        super().__init__(
            transport=httpx.ASGITransport(app=app), base_url="http://localhost:8080"
        )
