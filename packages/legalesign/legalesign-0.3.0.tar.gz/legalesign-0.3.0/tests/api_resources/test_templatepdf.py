# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from legalesign import Legalesign, AsyncLegalesign
from tests.utils import assert_matches_type
from legalesign.types import (
    TemplatePdf,
    TemplatepdfListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestTemplatepdf:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
            archive_upon_send=True,
            process_tags=True,
            title="title",
            user="user",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Legalesign) -> None:
        response = client.templatepdf.with_raw_response.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = response.parse()
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Legalesign) -> None:
        with client.templatepdf.with_streaming_response.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = response.parse()
            assert templatepdf is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TemplatePdf, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Legalesign) -> None:
        response = client.templatepdf.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = response.parse()
        assert_matches_type(TemplatePdf, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Legalesign) -> None:
        with client.templatepdf.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = response.parse()
            assert_matches_type(TemplatePdf, templatepdf, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            client.templatepdf.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.list()
        assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.list(
            archive="archive",
            group="group",
            limit=0,
            offset=0,
        )
        assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Legalesign) -> None:
        response = client.templatepdf.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = response.parse()
        assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Legalesign) -> None:
        with client.templatepdf.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = response.parse()
            assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_archive(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.archive(
            "pdfId",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_archive(self, client: Legalesign) -> None:
        response = client.templatepdf.with_raw_response.archive(
            "pdfId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = response.parse()
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_archive(self, client: Legalesign) -> None:
        with client.templatepdf.with_streaming_response.archive(
            "pdfId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = response.parse()
            assert templatepdf is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_archive(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            client.templatepdf.with_raw_response.archive(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_convert_tags(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.convert_tags(
            "pdfId",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_convert_tags(self, client: Legalesign) -> None:
        response = client.templatepdf.with_raw_response.convert_tags(
            "pdfId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = response.parse()
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_convert_tags(self, client: Legalesign) -> None:
        with client.templatepdf.with_streaming_response.convert_tags(
            "pdfId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = response.parse()
            assert templatepdf is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_convert_tags(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            client.templatepdf.with_raw_response.convert_tags(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_edit_link(self, client: Legalesign) -> None:
        templatepdf = client.templatepdf.get_edit_link(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_edit_link(self, client: Legalesign) -> None:
        response = client.templatepdf.with_raw_response.get_edit_link(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = response.parse()
        assert_matches_type(str, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_edit_link(self, client: Legalesign) -> None:
        with client.templatepdf.with_streaming_response.get_edit_link(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = response.parse()
            assert_matches_type(str, templatepdf, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_edit_link(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            client.templatepdf.with_raw_response.get_edit_link(
                "",
            )


class TestAsyncTemplatepdf:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
            archive_upon_send=True,
            process_tags=True,
            title="title",
            user="user",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.templatepdf.with_raw_response.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = await response.parse()
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLegalesign) -> None:
        async with async_client.templatepdf.with_streaming_response.create(
            group="/api/v1/group/IK-GV--w1tvt/",
            pdf_file="U3RhaW5sZXNzIHJvY2tz",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = await response.parse()
            assert templatepdf is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(TemplatePdf, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.templatepdf.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = await response.parse()
        assert_matches_type(TemplatePdf, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLegalesign) -> None:
        async with async_client.templatepdf.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = await response.parse()
            assert_matches_type(TemplatePdf, templatepdf, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            await async_client.templatepdf.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.list()
        assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.list(
            archive="archive",
            group="group",
            limit=0,
            offset=0,
        )
        assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.templatepdf.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = await response.parse()
        assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLegalesign) -> None:
        async with async_client.templatepdf.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = await response.parse()
            assert_matches_type(TemplatepdfListResponse, templatepdf, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_archive(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.archive(
            "pdfId",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_archive(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.templatepdf.with_raw_response.archive(
            "pdfId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = await response.parse()
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_archive(self, async_client: AsyncLegalesign) -> None:
        async with async_client.templatepdf.with_streaming_response.archive(
            "pdfId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = await response.parse()
            assert templatepdf is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_archive(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            await async_client.templatepdf.with_raw_response.archive(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_convert_tags(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.convert_tags(
            "pdfId",
        )
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_convert_tags(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.templatepdf.with_raw_response.convert_tags(
            "pdfId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = await response.parse()
        assert templatepdf is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_convert_tags(self, async_client: AsyncLegalesign) -> None:
        async with async_client.templatepdf.with_streaming_response.convert_tags(
            "pdfId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = await response.parse()
            assert templatepdf is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_convert_tags(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            await async_client.templatepdf.with_raw_response.convert_tags(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_edit_link(self, async_client: AsyncLegalesign) -> None:
        templatepdf = await async_client.templatepdf.get_edit_link(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(str, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_edit_link(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.templatepdf.with_raw_response.get_edit_link(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        templatepdf = await response.parse()
        assert_matches_type(str, templatepdf, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_edit_link(self, async_client: AsyncLegalesign) -> None:
        async with async_client.templatepdf.with_streaming_response.get_edit_link(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            templatepdf = await response.parse()
            assert_matches_type(str, templatepdf, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_edit_link(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `pdf_id` but received ''"):
            await async_client.templatepdf.with_raw_response.get_edit_link(
                "",
            )
