# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from legalesign import Legalesign, AsyncLegalesign
from tests.utils import assert_matches_type
from legalesign.types import (
    SignerRetrieveResponse,
    SignerRetrieveFieldsResponse,
    SignerGetRejectionReasonResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSigner:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Legalesign) -> None:
        signer = client.signer.retrieve(
            "signerId",
        )
        assert_matches_type(SignerRetrieveResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Legalesign) -> None:
        response = client.signer.with_raw_response.retrieve(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = response.parse()
        assert_matches_type(SignerRetrieveResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Legalesign) -> None:
        with client.signer.with_streaming_response.retrieve(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = response.parse()
            assert_matches_type(SignerRetrieveResponse, signer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            client.signer.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_access_link(self, client: Legalesign) -> None:
        signer = client.signer.get_access_link(
            "signerId",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_access_link(self, client: Legalesign) -> None:
        response = client.signer.with_raw_response.get_access_link(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = response.parse()
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_access_link(self, client: Legalesign) -> None:
        with client.signer.with_streaming_response.get_access_link(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = response.parse()
            assert signer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_access_link(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            client.signer.with_raw_response.get_access_link(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_rejection_reason(self, client: Legalesign) -> None:
        signer = client.signer.get_rejection_reason(
            "signerId",
        )
        assert_matches_type(SignerGetRejectionReasonResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_rejection_reason(self, client: Legalesign) -> None:
        response = client.signer.with_raw_response.get_rejection_reason(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = response.parse()
        assert_matches_type(SignerGetRejectionReasonResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_rejection_reason(self, client: Legalesign) -> None:
        with client.signer.with_streaming_response.get_rejection_reason(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = response.parse()
            assert_matches_type(SignerGetRejectionReasonResponse, signer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_rejection_reason(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            client.signer.with_raw_response.get_rejection_reason(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reset(self, client: Legalesign) -> None:
        signer = client.signer.reset(
            signer_id="signerId",
            email="email",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_reset_with_all_params(self, client: Legalesign) -> None:
        signer = client.signer.reset(
            signer_id="signerId",
            email="email",
            notify=True,
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_reset(self, client: Legalesign) -> None:
        response = client.signer.with_raw_response.reset(
            signer_id="signerId",
            email="email",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = response.parse()
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_reset(self, client: Legalesign) -> None:
        with client.signer.with_streaming_response.reset(
            signer_id="signerId",
            email="email",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = response.parse()
            assert signer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_reset(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            client.signer.with_raw_response.reset(
                signer_id="",
                email="email",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_fields(self, client: Legalesign) -> None:
        signer = client.signer.retrieve_fields(
            "signerId",
        )
        assert_matches_type(SignerRetrieveFieldsResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_fields(self, client: Legalesign) -> None:
        response = client.signer.with_raw_response.retrieve_fields(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = response.parse()
        assert_matches_type(SignerRetrieveFieldsResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_fields(self, client: Legalesign) -> None:
        with client.signer.with_streaming_response.retrieve_fields(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = response.parse()
            assert_matches_type(SignerRetrieveFieldsResponse, signer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_fields(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            client.signer.with_raw_response.retrieve_fields(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_reminder(self, client: Legalesign) -> None:
        signer = client.signer.send_reminder(
            signer_id="signerId",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_send_reminder_with_all_params(self, client: Legalesign) -> None:
        signer = client.signer.send_reminder(
            signer_id="signerId",
            text="text",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_send_reminder(self, client: Legalesign) -> None:
        response = client.signer.with_raw_response.send_reminder(
            signer_id="signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = response.parse()
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_send_reminder(self, client: Legalesign) -> None:
        with client.signer.with_streaming_response.send_reminder(
            signer_id="signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = response.parse()
            assert signer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_send_reminder(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            client.signer.with_raw_response.send_reminder(
                signer_id="",
            )


class TestAsyncSigner:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.retrieve(
            "signerId",
        )
        assert_matches_type(SignerRetrieveResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.signer.with_raw_response.retrieve(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = await response.parse()
        assert_matches_type(SignerRetrieveResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLegalesign) -> None:
        async with async_client.signer.with_streaming_response.retrieve(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = await response.parse()
            assert_matches_type(SignerRetrieveResponse, signer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            await async_client.signer.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_access_link(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.get_access_link(
            "signerId",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_access_link(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.signer.with_raw_response.get_access_link(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = await response.parse()
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_access_link(self, async_client: AsyncLegalesign) -> None:
        async with async_client.signer.with_streaming_response.get_access_link(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = await response.parse()
            assert signer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_access_link(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            await async_client.signer.with_raw_response.get_access_link(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_rejection_reason(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.get_rejection_reason(
            "signerId",
        )
        assert_matches_type(SignerGetRejectionReasonResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_rejection_reason(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.signer.with_raw_response.get_rejection_reason(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = await response.parse()
        assert_matches_type(SignerGetRejectionReasonResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_rejection_reason(self, async_client: AsyncLegalesign) -> None:
        async with async_client.signer.with_streaming_response.get_rejection_reason(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = await response.parse()
            assert_matches_type(SignerGetRejectionReasonResponse, signer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_rejection_reason(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            await async_client.signer.with_raw_response.get_rejection_reason(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reset(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.reset(
            signer_id="signerId",
            email="email",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_reset_with_all_params(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.reset(
            signer_id="signerId",
            email="email",
            notify=True,
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_reset(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.signer.with_raw_response.reset(
            signer_id="signerId",
            email="email",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = await response.parse()
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_reset(self, async_client: AsyncLegalesign) -> None:
        async with async_client.signer.with_streaming_response.reset(
            signer_id="signerId",
            email="email",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = await response.parse()
            assert signer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_reset(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            await async_client.signer.with_raw_response.reset(
                signer_id="",
                email="email",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_fields(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.retrieve_fields(
            "signerId",
        )
        assert_matches_type(SignerRetrieveFieldsResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_fields(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.signer.with_raw_response.retrieve_fields(
            "signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = await response.parse()
        assert_matches_type(SignerRetrieveFieldsResponse, signer, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_fields(self, async_client: AsyncLegalesign) -> None:
        async with async_client.signer.with_streaming_response.retrieve_fields(
            "signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = await response.parse()
            assert_matches_type(SignerRetrieveFieldsResponse, signer, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_fields(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            await async_client.signer.with_raw_response.retrieve_fields(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_reminder(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.send_reminder(
            signer_id="signerId",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_send_reminder_with_all_params(self, async_client: AsyncLegalesign) -> None:
        signer = await async_client.signer.send_reminder(
            signer_id="signerId",
            text="text",
        )
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_send_reminder(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.signer.with_raw_response.send_reminder(
            signer_id="signerId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signer = await response.parse()
        assert signer is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_send_reminder(self, async_client: AsyncLegalesign) -> None:
        async with async_client.signer.with_streaming_response.send_reminder(
            signer_id="signerId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signer = await response.parse()
            assert signer is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_send_reminder(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `signer_id` but received ''"):
            await async_client.signer.with_raw_response.send_reminder(
                signer_id="",
            )
