# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from legalesign import Legalesign, AsyncLegalesign
from legalesign._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPdf:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_retrieve(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/pdf/docId/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        pdf = client.pdf.retrieve(
            "docId",
        )
        assert pdf.is_closed
        assert pdf.json() == {"foo": "bar"}
        assert cast(Any, pdf.is_closed) is True
        assert isinstance(pdf, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_retrieve(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/pdf/docId/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        pdf = client.pdf.with_raw_response.retrieve(
            "docId",
        )

        assert pdf.is_closed is True
        assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"
        assert pdf.json() == {"foo": "bar"}
        assert isinstance(pdf, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_retrieve(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/pdf/docId/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.pdf.with_streaming_response.retrieve(
            "docId",
        ) as pdf:
            assert not pdf.is_closed
            assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"

            assert pdf.json() == {"foo": "bar"}
            assert cast(Any, pdf.is_closed) is True
            assert isinstance(pdf, StreamedBinaryAPIResponse)

        assert cast(Any, pdf.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_retrieve(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.pdf.with_raw_response.retrieve(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_preview(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        pdf = client.pdf.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
        )
        assert pdf.is_closed
        assert pdf.json() == {"foo": "bar"}
        assert cast(Any, pdf.is_closed) is True
        assert isinstance(pdf, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_create_preview_with_all_params(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        pdf = client.pdf.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
            footer="footer",
            footer_height=0,
            header="header",
            header_height=0,
            pdfheader=True,
            title="title",
        )
        assert pdf.is_closed
        assert pdf.json() == {"foo": "bar"}
        assert cast(Any, pdf.is_closed) is True
        assert isinstance(pdf, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_create_preview(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        pdf = client.pdf.with_raw_response.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
        )

        assert pdf.is_closed is True
        assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"
        assert pdf.json() == {"foo": "bar"}
        assert isinstance(pdf, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_create_preview(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.pdf.with_streaming_response.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
        ) as pdf:
            assert not pdf.is_closed
            assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"

            assert pdf.json() == {"foo": "bar"}
            assert cast(Any, pdf.is_closed) is True
            assert isinstance(pdf, StreamedBinaryAPIResponse)

        assert cast(Any, pdf.is_closed) is True


class TestAsyncPdf:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_retrieve(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/pdf/docId/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        pdf = await async_client.pdf.retrieve(
            "docId",
        )
        assert pdf.is_closed
        assert await pdf.json() == {"foo": "bar"}
        assert cast(Any, pdf.is_closed) is True
        assert isinstance(pdf, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_retrieve(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/pdf/docId/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        pdf = await async_client.pdf.with_raw_response.retrieve(
            "docId",
        )

        assert pdf.is_closed is True
        assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await pdf.json() == {"foo": "bar"}
        assert isinstance(pdf, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_retrieve(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/pdf/docId/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.pdf.with_streaming_response.retrieve(
            "docId",
        ) as pdf:
            assert not pdf.is_closed
            assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await pdf.json() == {"foo": "bar"}
            assert cast(Any, pdf.is_closed) is True
            assert isinstance(pdf, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, pdf.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_retrieve(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.pdf.with_raw_response.retrieve(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_preview(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        pdf = await async_client.pdf.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
        )
        assert pdf.is_closed
        assert await pdf.json() == {"foo": "bar"}
        assert cast(Any, pdf.is_closed) is True
        assert isinstance(pdf, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_create_preview_with_all_params(
        self, async_client: AsyncLegalesign, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        pdf = await async_client.pdf.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
            footer="footer",
            footer_height=0,
            header="header",
            header_height=0,
            pdfheader=True,
            title="title",
        )
        assert pdf.is_closed
        assert await pdf.json() == {"foo": "bar"}
        assert cast(Any, pdf.is_closed) is True
        assert isinstance(pdf, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_create_preview(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        pdf = await async_client.pdf.with_raw_response.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
        )

        assert pdf.is_closed is True
        assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await pdf.json() == {"foo": "bar"}
        assert isinstance(pdf, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_create_preview(
        self, async_client: AsyncLegalesign, respx_mock: MockRouter
    ) -> None:
        respx_mock.post("/pdf/preview/").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.pdf.with_streaming_response.create_preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            is_signature_per_page=0,
            signature_type=0,
            signee_count=0,
            text="text",
        ) as pdf:
            assert not pdf.is_closed
            assert pdf.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await pdf.json() == {"foo": "bar"}
            assert cast(Any, pdf.is_closed) is True
            assert isinstance(pdf, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, pdf.is_closed) is True
