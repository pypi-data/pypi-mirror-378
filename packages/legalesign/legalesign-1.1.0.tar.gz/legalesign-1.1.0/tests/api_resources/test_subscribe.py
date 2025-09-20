# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from legalesign import Legalesign, AsyncLegalesign

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSubscribe:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_webhook(self, client: Legalesign) -> None:
        subscribe = client.subscribe.create_webhook(
            notify="realtime",
            url="https://",
        )
        assert subscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_webhook_with_all_params(self, client: Legalesign) -> None:
        subscribe = client.subscribe.create_webhook(
            notify="realtime",
            url="https://",
            event_filter="",
            group="group",
        )
        assert subscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_webhook(self, client: Legalesign) -> None:
        response = client.subscribe.with_raw_response.create_webhook(
            notify="realtime",
            url="https://",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscribe = response.parse()
        assert subscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_webhook(self, client: Legalesign) -> None:
        with client.subscribe.with_streaming_response.create_webhook(
            notify="realtime",
            url="https://",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscribe = response.parse()
            assert subscribe is None

        assert cast(Any, response.is_closed) is True


class TestAsyncSubscribe:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_webhook(self, async_client: AsyncLegalesign) -> None:
        subscribe = await async_client.subscribe.create_webhook(
            notify="realtime",
            url="https://",
        )
        assert subscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_webhook_with_all_params(self, async_client: AsyncLegalesign) -> None:
        subscribe = await async_client.subscribe.create_webhook(
            notify="realtime",
            url="https://",
            event_filter="",
            group="group",
        )
        assert subscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_webhook(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.subscribe.with_raw_response.create_webhook(
            notify="realtime",
            url="https://",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        subscribe = await response.parse()
        assert subscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_webhook(self, async_client: AsyncLegalesign) -> None:
        async with async_client.subscribe.with_streaming_response.create_webhook(
            notify="realtime",
            url="https://",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            subscribe = await response.parse()
            assert subscribe is None

        assert cast(Any, response.is_closed) is True
