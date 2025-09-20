# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from legalesign import Legalesign, AsyncLegalesign

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUnsubscribe:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_webhook(self, client: Legalesign) -> None:
        unsubscribe = client.unsubscribe.delete_webhook(
            url="https://",
        )
        assert unsubscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_webhook_with_all_params(self, client: Legalesign) -> None:
        unsubscribe = client.unsubscribe.delete_webhook(
            url="https://",
            event_filter="",
            group=0,
        )
        assert unsubscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_webhook(self, client: Legalesign) -> None:
        response = client.unsubscribe.with_raw_response.delete_webhook(
            url="https://",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        unsubscribe = response.parse()
        assert unsubscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_webhook(self, client: Legalesign) -> None:
        with client.unsubscribe.with_streaming_response.delete_webhook(
            url="https://",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            unsubscribe = response.parse()
            assert unsubscribe is None

        assert cast(Any, response.is_closed) is True


class TestAsyncUnsubscribe:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_webhook(self, async_client: AsyncLegalesign) -> None:
        unsubscribe = await async_client.unsubscribe.delete_webhook(
            url="https://",
        )
        assert unsubscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_webhook_with_all_params(self, async_client: AsyncLegalesign) -> None:
        unsubscribe = await async_client.unsubscribe.delete_webhook(
            url="https://",
            event_filter="",
            group=0,
        )
        assert unsubscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_webhook(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.unsubscribe.with_raw_response.delete_webhook(
            url="https://",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        unsubscribe = await response.parse()
        assert unsubscribe is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_webhook(self, async_client: AsyncLegalesign) -> None:
        async with async_client.unsubscribe.with_streaming_response.delete_webhook(
            url="https://",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            unsubscribe = await response.parse()
            assert unsubscribe is None

        assert cast(Any, response.is_closed) is True
