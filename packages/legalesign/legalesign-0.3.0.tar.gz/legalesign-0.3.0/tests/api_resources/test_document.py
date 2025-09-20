# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from legalesign import Legalesign, AsyncLegalesign
from tests.utils import assert_matches_type
from legalesign.types import (
    DocumentListResponse,
    DocumentCreateResponse,
    DocumentRetrieveResponse,
    DocumentGetFieldsResponse,
)
from legalesign._utils import parse_datetime
from legalesign._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDocument:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Legalesign) -> None:
        document = client.document.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                }
            ],
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Legalesign) -> None:
        document = client.document.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                    "attachments": ["/api/v1/attachment/IK-GV--w1tvt/"],
                    "behalfof": "behalfof",
                    "decide_later": True,
                    "expires": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "message": "message",
                    "order": 0,
                    "reviewers": [
                        {
                            "email": "dev@stainless.com",
                            "firstname": "firstname",
                            "include_link": True,
                            "lastname": "lastname",
                        }
                    ],
                    "role": "witness",
                    "sms": "sms",
                    "subject": "subject",
                    "timezone": "timezone",
                }
            ],
            append_pdf=True,
            auto_archive=True,
            cc_emails="cc_emails",
            convert_sender_to_signer=True,
            do_email=True,
            footer="footer",
            footer_height=0,
            header="header",
            header_height=0,
            pdf_password="pdf_password",
            pdf_password_type=1,
            pdftext={"foo": "string"},
            redirect="https://",
            reminders="",
            return_signer_links=True,
            signature_type=0,
            signers_in_order=True,
            signertext={"foo": "string"},
            strict_fields=True,
            tag="tag",
            tag1="tag1",
            tag2="tag2",
            template="https://example.com",
            templatepdf="https://example.com",
            text="text",
            user="https://example.com",
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentCreateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Legalesign) -> None:
        document = client.document.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.document.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Legalesign) -> None:
        document = client.document.list(
            group="group",
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Legalesign) -> None:
        document = client.document.list(
            group="group",
            archived="archived",
            created_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            email="email",
            limit=0,
            modified_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            nosigners="nosigners",
            offset=0,
            status=0,
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.list(
            group="group",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.list(
            group="group",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentListResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_archive(self, client: Legalesign) -> None:
        document = client.document.archive(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_archive(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.archive(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_archive(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.archive(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert document is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_archive(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.document.with_raw_response.archive(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete_permanently(self, client: Legalesign) -> None:
        document = client.document.delete_permanently(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete_permanently(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.delete_permanently(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete_permanently(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.delete_permanently(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert document is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete_permanently(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.document.with_raw_response.delete_permanently(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_audit_log(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/auditlog/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        document = client.document.download_audit_log(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document.is_closed
        assert document.json() == {"foo": "bar"}
        assert cast(Any, document.is_closed) is True
        assert isinstance(document, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download_audit_log(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/auditlog/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        document = client.document.with_raw_response.download_audit_log(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert document.is_closed is True
        assert document.http_request.headers.get("X-Stainless-Lang") == "python"
        assert document.json() == {"foo": "bar"}
        assert isinstance(document, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download_audit_log(self, client: Legalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/auditlog/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        with client.document.with_streaming_response.download_audit_log(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as document:
            assert not document.is_closed
            assert document.http_request.headers.get("X-Stainless-Lang") == "python"

            assert document.json() == {"foo": "bar"}
            assert cast(Any, document.is_closed) is True
            assert isinstance(document, StreamedBinaryAPIResponse)

        assert cast(Any, document.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download_audit_log(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.document.with_raw_response.download_audit_log(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_fields(self, client: Legalesign) -> None:
        document = client.document.get_fields(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetFieldsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_fields(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.get_fields(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert_matches_type(DocumentGetFieldsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_fields(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.get_fields(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert_matches_type(DocumentGetFieldsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_fields(self, client: Legalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            client.document.with_raw_response.get_fields(
                "",
            )

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_preview(self, client: Legalesign) -> None:
        document = client.document.preview()
        assert document is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_preview_with_all_params(self, client: Legalesign) -> None:
        document = client.document.preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            signee_count=0,
            text="text",
            title="title",
        )
        assert document is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_raw_response_preview(self, client: Legalesign) -> None:
        response = client.document.with_raw_response.preview()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = response.parse()
        assert document is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_streaming_response_preview(self, client: Legalesign) -> None:
        with client.document.with_streaming_response.preview() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = response.parse()
            assert document is None

        assert cast(Any, response.is_closed) is True


class TestAsyncDocument:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                }
            ],
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                    "attachments": ["/api/v1/attachment/IK-GV--w1tvt/"],
                    "behalfof": "behalfof",
                    "decide_later": True,
                    "expires": parse_datetime("2019-12-27T18:11:19.117Z"),
                    "message": "message",
                    "order": 0,
                    "reviewers": [
                        {
                            "email": "dev@stainless.com",
                            "firstname": "firstname",
                            "include_link": True,
                            "lastname": "lastname",
                        }
                    ],
                    "role": "witness",
                    "sms": "sms",
                    "subject": "subject",
                    "timezone": "timezone",
                }
            ],
            append_pdf=True,
            auto_archive=True,
            cc_emails="cc_emails",
            convert_sender_to_signer=True,
            do_email=True,
            footer="footer",
            footer_height=0,
            header="header",
            header_height=0,
            pdf_password="pdf_password",
            pdf_password_type=1,
            pdftext={"foo": "string"},
            redirect="https://",
            reminders="",
            return_signer_links=True,
            signature_type=0,
            signers_in_order=True,
            signertext={"foo": "string"},
            strict_fields=True,
            tag="tag",
            tag1="tag1",
            tag2="tag2",
            template="https://example.com",
            templatepdf="https://example.com",
            text="text",
            user="https://example.com",
        )
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                }
            ],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentCreateResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.create(
            group="https://example.com",
            name="x",
            signers=[
                {
                    "email": "dev@stainless.com",
                    "firstname": "firstname",
                    "lastname": "lastname",
                }
            ],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentCreateResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.retrieve(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentRetrieveResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.document.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.list(
            group="group",
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.list(
            group="group",
            archived="archived",
            created_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            email="email",
            limit=0,
            modified_gt=parse_datetime("2019-12-27T18:11:19.117Z"),
            nosigners="nosigners",
            offset=0,
            status=0,
        )
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.list(
            group="group",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentListResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.list(
            group="group",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentListResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_archive(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.archive(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_archive(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.archive(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_archive(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.archive(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert document is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_archive(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.document.with_raw_response.archive(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete_permanently(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.delete_permanently(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete_permanently(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.delete_permanently(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert document is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete_permanently(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.delete_permanently(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert document is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete_permanently(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.document.with_raw_response.delete_permanently(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_audit_log(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/auditlog/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        document = await async_client.document.download_audit_log(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert document.is_closed
        assert await document.json() == {"foo": "bar"}
        assert cast(Any, document.is_closed) is True
        assert isinstance(document, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download_audit_log(self, async_client: AsyncLegalesign, respx_mock: MockRouter) -> None:
        respx_mock.get("/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/auditlog/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )

        document = await async_client.document.with_raw_response.download_audit_log(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert document.is_closed is True
        assert document.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await document.json() == {"foo": "bar"}
        assert isinstance(document, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download_audit_log(
        self, async_client: AsyncLegalesign, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/document/182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e/auditlog/").mock(
            return_value=httpx.Response(200, json={"foo": "bar"})
        )
        async with async_client.document.with_streaming_response.download_audit_log(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as document:
            assert not document.is_closed
            assert document.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await document.json() == {"foo": "bar"}
            assert cast(Any, document.is_closed) is True
            assert isinstance(document, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, document.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download_audit_log(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.document.with_raw_response.download_audit_log(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_fields(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.get_fields(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )
        assert_matches_type(DocumentGetFieldsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_fields(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.get_fields(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert_matches_type(DocumentGetFieldsResponse, document, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_fields(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.get_fields(
            "182bd5e5-6e1a-4fe4-a799-aa6d9a6ab26e",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert_matches_type(DocumentGetFieldsResponse, document, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_fields(self, async_client: AsyncLegalesign) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `doc_id` but received ''"):
            await async_client.document.with_raw_response.get_fields(
                "",
            )

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_preview(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.preview()
        assert document is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_preview_with_all_params(self, async_client: AsyncLegalesign) -> None:
        document = await async_client.document.preview(
            group="/api/v1/group/IK-GV--w1tvt/",
            signee_count=0,
            text="text",
            title="title",
        )
        assert document is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_raw_response_preview(self, async_client: AsyncLegalesign) -> None:
        response = await async_client.document.with_raw_response.preview()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        document = await response.parse()
        assert document is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_streaming_response_preview(self, async_client: AsyncLegalesign) -> None:
        async with async_client.document.with_streaming_response.preview() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            document = await response.parse()
            assert document is None

        assert cast(Any, response.is_closed) is True
