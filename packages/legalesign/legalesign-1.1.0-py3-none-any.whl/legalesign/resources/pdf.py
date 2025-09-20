# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import pdf_create_preview_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_custom_raw_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["PdfResource", "AsyncPdfResource"]


class PdfResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> PdfResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return PdfResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> PdfResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return PdfResourceWithStreamingResponse(self)

    def retrieve(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        Get the PDF for a signing document

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "application/pdf", **(extra_headers or {})}
        return self._get(
            f"/pdf/{doc_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def create_preview(
        self,
        *,
        group: str,
        is_signature_per_page: int,
        signature_type: int,
        signee_count: int,
        text: str,
        footer: str | Omit = omit,
        footer_height: int | Omit = omit,
        header: str | Omit = omit,
        header_height: int | Omit = omit,
        pdfheader: bool | Omit = omit,
        title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> BinaryAPIResponse:
        """
        text/html document as pdf preview

        Args:
          signee_count: number of signers

          text: raw html

          pdfheader: Set to true to use group default

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/pdf", **(extra_headers or {})}
        return self._post(
            "/pdf/preview/",
            body=maybe_transform(
                {
                    "group": group,
                    "is_signature_per_page": is_signature_per_page,
                    "signature_type": signature_type,
                    "signee_count": signee_count,
                    "text": text,
                    "footer": footer,
                    "footer_height": footer_height,
                    "header": header,
                    "header_height": header_height,
                    "pdfheader": pdfheader,
                    "title": title,
                },
                pdf_create_preview_params.PdfCreatePreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncPdfResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncPdfResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncPdfResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncPdfResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncPdfResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        Get the PDF for a signing document

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "application/pdf", **(extra_headers or {})}
        return await self._get(
            f"/pdf/{doc_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def create_preview(
        self,
        *,
        group: str,
        is_signature_per_page: int,
        signature_type: int,
        signee_count: int,
        text: str,
        footer: str | Omit = omit,
        footer_height: int | Omit = omit,
        header: str | Omit = omit,
        header_height: int | Omit = omit,
        pdfheader: bool | Omit = omit,
        title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AsyncBinaryAPIResponse:
        """
        text/html document as pdf preview

        Args:
          signee_count: number of signers

          text: raw html

          pdfheader: Set to true to use group default

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "application/pdf", **(extra_headers or {})}
        return await self._post(
            "/pdf/preview/",
            body=await async_maybe_transform(
                {
                    "group": group,
                    "is_signature_per_page": is_signature_per_page,
                    "signature_type": signature_type,
                    "signee_count": signee_count,
                    "text": text,
                    "footer": footer,
                    "footer_height": footer_height,
                    "header": header,
                    "header_height": header_height,
                    "pdfheader": pdfheader,
                    "title": title,
                },
                pdf_create_preview_params.PdfCreatePreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class PdfResourceWithRawResponse:
    def __init__(self, pdf: PdfResource) -> None:
        self._pdf = pdf

        self.retrieve = to_custom_raw_response_wrapper(
            pdf.retrieve,
            BinaryAPIResponse,
        )
        self.create_preview = to_custom_raw_response_wrapper(
            pdf.create_preview,
            BinaryAPIResponse,
        )


class AsyncPdfResourceWithRawResponse:
    def __init__(self, pdf: AsyncPdfResource) -> None:
        self._pdf = pdf

        self.retrieve = async_to_custom_raw_response_wrapper(
            pdf.retrieve,
            AsyncBinaryAPIResponse,
        )
        self.create_preview = async_to_custom_raw_response_wrapper(
            pdf.create_preview,
            AsyncBinaryAPIResponse,
        )


class PdfResourceWithStreamingResponse:
    def __init__(self, pdf: PdfResource) -> None:
        self._pdf = pdf

        self.retrieve = to_custom_streamed_response_wrapper(
            pdf.retrieve,
            StreamedBinaryAPIResponse,
        )
        self.create_preview = to_custom_streamed_response_wrapper(
            pdf.create_preview,
            StreamedBinaryAPIResponse,
        )


class AsyncPdfResourceWithStreamingResponse:
    def __init__(self, pdf: AsyncPdfResource) -> None:
        self._pdf = pdf

        self.retrieve = async_to_custom_streamed_response_wrapper(
            pdf.retrieve,
            AsyncStreamedBinaryAPIResponse,
        )
        self.create_preview = async_to_custom_streamed_response_wrapper(
            pdf.create_preview,
            AsyncStreamedBinaryAPIResponse,
        )
