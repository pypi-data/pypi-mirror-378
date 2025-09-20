# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union

import httpx

from ..types import attachment_list_params, attachment_upload_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, Base64FileInput, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.attachment_response import AttachmentResponse
from ..types.attachment_list_response import AttachmentListResponse

__all__ = ["AttachmentResource", "AsyncAttachmentResource"]


class AttachmentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AttachmentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AttachmentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AttachmentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AttachmentResourceWithStreamingResponse(self)

    def retrieve(
        self,
        attachment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttachmentResponse:
        """
        Get attachment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not attachment_id:
            raise ValueError(f"Expected a non-empty value for `attachment_id` but received {attachment_id!r}")
        return self._get(
            f"/attachment/{attachment_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AttachmentResponse,
        )

    def list(
        self,
        *,
        group: str | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttachmentListResponse:
        """
        List attachments in your groups

        Args:
          group: Filter by a specific group

          limit: Length of dataset to return. Use with offset query to iterate through results.

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/attachment/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group": group,
                        "limit": limit,
                        "offset": offset,
                    },
                    attachment_list_params.AttachmentListParams,
                ),
            ),
            cast_to=AttachmentListResponse,
        )

    def delete(
        self,
        attachment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete attachment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not attachment_id:
            raise ValueError(f"Expected a non-empty value for `attachment_id` but received {attachment_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/attachment/{attachment_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def upload(
        self,
        *,
        filename: str,
        group: str,
        pdf_file: Union[str, Base64FileInput],
        description: str | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Upload PDF attachment

        Args:
          filename: Simple alphanumeric name ending .pdf

          group: URI of the group name

          pdf_file: Base64 encoded PDF file data, max size is a group setting, 5MB by default

          user: Assign to group member if not the api user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/attachment/",
            body=maybe_transform(
                {
                    "filename": filename,
                    "group": group,
                    "pdf_file": pdf_file,
                    "description": description,
                    "user": user,
                },
                attachment_upload_params.AttachmentUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAttachmentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAttachmentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAttachmentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAttachmentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncAttachmentResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        attachment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttachmentResponse:
        """
        Get attachment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not attachment_id:
            raise ValueError(f"Expected a non-empty value for `attachment_id` but received {attachment_id!r}")
        return await self._get(
            f"/attachment/{attachment_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AttachmentResponse,
        )

    async def list(
        self,
        *,
        group: str | Omit = omit,
        limit: int | Omit = omit,
        offset: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttachmentListResponse:
        """
        List attachments in your groups

        Args:
          group: Filter by a specific group

          limit: Length of dataset to return. Use with offset query to iterate through results.

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/attachment/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group": group,
                        "limit": limit,
                        "offset": offset,
                    },
                    attachment_list_params.AttachmentListParams,
                ),
            ),
            cast_to=AttachmentListResponse,
        )

    async def delete(
        self,
        attachment_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete attachment

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not attachment_id:
            raise ValueError(f"Expected a non-empty value for `attachment_id` but received {attachment_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/attachment/{attachment_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def upload(
        self,
        *,
        filename: str,
        group: str,
        pdf_file: Union[str, Base64FileInput],
        description: str | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Upload PDF attachment

        Args:
          filename: Simple alphanumeric name ending .pdf

          group: URI of the group name

          pdf_file: Base64 encoded PDF file data, max size is a group setting, 5MB by default

          user: Assign to group member if not the api user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/attachment/",
            body=await async_maybe_transform(
                {
                    "filename": filename,
                    "group": group,
                    "pdf_file": pdf_file,
                    "description": description,
                    "user": user,
                },
                attachment_upload_params.AttachmentUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AttachmentResourceWithRawResponse:
    def __init__(self, attachment: AttachmentResource) -> None:
        self._attachment = attachment

        self.retrieve = to_raw_response_wrapper(
            attachment.retrieve,
        )
        self.list = to_raw_response_wrapper(
            attachment.list,
        )
        self.delete = to_raw_response_wrapper(
            attachment.delete,
        )
        self.upload = to_raw_response_wrapper(
            attachment.upload,
        )


class AsyncAttachmentResourceWithRawResponse:
    def __init__(self, attachment: AsyncAttachmentResource) -> None:
        self._attachment = attachment

        self.retrieve = async_to_raw_response_wrapper(
            attachment.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            attachment.list,
        )
        self.delete = async_to_raw_response_wrapper(
            attachment.delete,
        )
        self.upload = async_to_raw_response_wrapper(
            attachment.upload,
        )


class AttachmentResourceWithStreamingResponse:
    def __init__(self, attachment: AttachmentResource) -> None:
        self._attachment = attachment

        self.retrieve = to_streamed_response_wrapper(
            attachment.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            attachment.list,
        )
        self.delete = to_streamed_response_wrapper(
            attachment.delete,
        )
        self.upload = to_streamed_response_wrapper(
            attachment.upload,
        )


class AsyncAttachmentResourceWithStreamingResponse:
    def __init__(self, attachment: AsyncAttachmentResource) -> None:
        self._attachment = attachment

        self.retrieve = async_to_streamed_response_wrapper(
            attachment.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            attachment.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            attachment.delete,
        )
        self.upload = async_to_streamed_response_wrapper(
            attachment.upload,
        )
