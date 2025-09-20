# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union

import httpx

from .fields import (
    FieldsResource,
    AsyncFieldsResource,
    FieldsResourceWithRawResponse,
    AsyncFieldsResourceWithRawResponse,
    FieldsResourceWithStreamingResponse,
    AsyncFieldsResourceWithStreamingResponse,
)
from ...types import templatepdf_list_params, templatepdf_create_params
from ..._types import Body, Omit, Query, Headers, NoneType, NotGiven, Base64FileInput, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.template_pdf import TemplatePdf
from ...types.templatepdf_list_response import TemplatepdfListResponse

__all__ = ["TemplatepdfResource", "AsyncTemplatepdfResource"]


class TemplatepdfResource(SyncAPIResource):
    @cached_property
    def fields(self) -> FieldsResource:
        return FieldsResource(self._client)

    @cached_property
    def with_raw_response(self) -> TemplatepdfResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return TemplatepdfResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TemplatepdfResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return TemplatepdfResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        group: str,
        pdf_file: Union[str, Base64FileInput],
        archive_upon_send: bool | Omit = omit,
        process_tags: bool | Omit = omit,
        title: str | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Upload a PDF document you want to send to be signed

        Args:
          pdf_file: base64 encoded PDF file data

          archive_upon_send: archive PDF when sent

          user: assign to group member if not api user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/templatepdf/",
            body=maybe_transform(
                {
                    "group": group,
                    "pdf_file": pdf_file,
                    "archive_upon_send": archive_upon_send,
                    "process_tags": process_tags,
                    "title": title,
                    "user": user,
                },
                templatepdf_create_params.TemplatepdfCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TemplatePdf:
        """
        Get PDF template

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        return self._get(
            f"/templatepdf/{pdf_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TemplatePdf,
        )

    def list(
        self,
        *,
        archive: str | Omit = omit,
        group: str | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TemplatepdfListResponse:
        """
        Get PDF templates

        Args:
          group: can be full resource_uri or only id

          limit: Length of dataset to return. Use with offset query to iterate through results.

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/templatepdf/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "archive": archive,
                        "group": group,
                        "limit": limit,
                        "offset": offset,
                    },
                    templatepdf_list_params.TemplatepdfListParams,
                ),
            ),
            cast_to=TemplatepdfListResponse,
        )

    def archive(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delists the PDF

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/templatepdf/{pdf_id}/archive/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def convert_tags(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Convert any text tags in the PDF into fields

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/templatepdf/{pdf_id}/tags/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_edit_link(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> str:
        """
        Get PDF embeddable link

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        return self._get(
            f"/templatepdf/{pdf_id}/edit-link/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class AsyncTemplatepdfResource(AsyncAPIResource):
    @cached_property
    def fields(self) -> AsyncFieldsResource:
        return AsyncFieldsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTemplatepdfResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTemplatepdfResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTemplatepdfResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncTemplatepdfResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        group: str,
        pdf_file: Union[str, Base64FileInput],
        archive_upon_send: bool | Omit = omit,
        process_tags: bool | Omit = omit,
        title: str | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Upload a PDF document you want to send to be signed

        Args:
          pdf_file: base64 encoded PDF file data

          archive_upon_send: archive PDF when sent

          user: assign to group member if not api user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/templatepdf/",
            body=await async_maybe_transform(
                {
                    "group": group,
                    "pdf_file": pdf_file,
                    "archive_upon_send": archive_upon_send,
                    "process_tags": process_tags,
                    "title": title,
                    "user": user,
                },
                templatepdf_create_params.TemplatepdfCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TemplatePdf:
        """
        Get PDF template

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        return await self._get(
            f"/templatepdf/{pdf_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TemplatePdf,
        )

    async def list(
        self,
        *,
        archive: str | Omit = omit,
        group: str | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TemplatepdfListResponse:
        """
        Get PDF templates

        Args:
          group: can be full resource_uri or only id

          limit: Length of dataset to return. Use with offset query to iterate through results.

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/templatepdf/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "archive": archive,
                        "group": group,
                        "limit": limit,
                        "offset": offset,
                    },
                    templatepdf_list_params.TemplatepdfListParams,
                ),
            ),
            cast_to=TemplatepdfListResponse,
        )

    async def archive(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delists the PDF

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/templatepdf/{pdf_id}/archive/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def convert_tags(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Convert any text tags in the PDF into fields

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/templatepdf/{pdf_id}/tags/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_edit_link(
        self,
        pdf_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> str:
        """
        Get PDF embeddable link

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not pdf_id:
            raise ValueError(f"Expected a non-empty value for `pdf_id` but received {pdf_id!r}")
        return await self._get(
            f"/templatepdf/{pdf_id}/edit-link/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )


class TemplatepdfResourceWithRawResponse:
    def __init__(self, templatepdf: TemplatepdfResource) -> None:
        self._templatepdf = templatepdf

        self.create = to_raw_response_wrapper(
            templatepdf.create,
        )
        self.retrieve = to_raw_response_wrapper(
            templatepdf.retrieve,
        )
        self.list = to_raw_response_wrapper(
            templatepdf.list,
        )
        self.archive = to_raw_response_wrapper(
            templatepdf.archive,
        )
        self.convert_tags = to_raw_response_wrapper(
            templatepdf.convert_tags,
        )
        self.get_edit_link = to_raw_response_wrapper(
            templatepdf.get_edit_link,
        )

    @cached_property
    def fields(self) -> FieldsResourceWithRawResponse:
        return FieldsResourceWithRawResponse(self._templatepdf.fields)


class AsyncTemplatepdfResourceWithRawResponse:
    def __init__(self, templatepdf: AsyncTemplatepdfResource) -> None:
        self._templatepdf = templatepdf

        self.create = async_to_raw_response_wrapper(
            templatepdf.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            templatepdf.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            templatepdf.list,
        )
        self.archive = async_to_raw_response_wrapper(
            templatepdf.archive,
        )
        self.convert_tags = async_to_raw_response_wrapper(
            templatepdf.convert_tags,
        )
        self.get_edit_link = async_to_raw_response_wrapper(
            templatepdf.get_edit_link,
        )

    @cached_property
    def fields(self) -> AsyncFieldsResourceWithRawResponse:
        return AsyncFieldsResourceWithRawResponse(self._templatepdf.fields)


class TemplatepdfResourceWithStreamingResponse:
    def __init__(self, templatepdf: TemplatepdfResource) -> None:
        self._templatepdf = templatepdf

        self.create = to_streamed_response_wrapper(
            templatepdf.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            templatepdf.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            templatepdf.list,
        )
        self.archive = to_streamed_response_wrapper(
            templatepdf.archive,
        )
        self.convert_tags = to_streamed_response_wrapper(
            templatepdf.convert_tags,
        )
        self.get_edit_link = to_streamed_response_wrapper(
            templatepdf.get_edit_link,
        )

    @cached_property
    def fields(self) -> FieldsResourceWithStreamingResponse:
        return FieldsResourceWithStreamingResponse(self._templatepdf.fields)


class AsyncTemplatepdfResourceWithStreamingResponse:
    def __init__(self, templatepdf: AsyncTemplatepdfResource) -> None:
        self._templatepdf = templatepdf

        self.create = async_to_streamed_response_wrapper(
            templatepdf.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            templatepdf.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            templatepdf.list,
        )
        self.archive = async_to_streamed_response_wrapper(
            templatepdf.archive,
        )
        self.convert_tags = async_to_streamed_response_wrapper(
            templatepdf.convert_tags,
        )
        self.get_edit_link = async_to_streamed_response_wrapper(
            templatepdf.get_edit_link,
        )

    @cached_property
    def fields(self) -> AsyncFieldsResourceWithStreamingResponse:
        return AsyncFieldsResourceWithStreamingResponse(self._templatepdf.fields)
