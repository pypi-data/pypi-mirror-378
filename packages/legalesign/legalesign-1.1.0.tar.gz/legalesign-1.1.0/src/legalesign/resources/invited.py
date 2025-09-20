# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import invited_list_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
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
from ..types.invited_list_response import InvitedListResponse

__all__ = ["InvitedResource", "AsyncInvitedResource"]


class InvitedResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> InvitedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return InvitedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> InvitedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return InvitedResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        group: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InvitedListResponse:
        """
        Invitations to people to join the group are listed by email

        Args:
          group: filter list by a given group

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/invited/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"group": group}, invited_list_params.InvitedListParams),
            ),
            cast_to=InvitedListResponse,
        )

    def delete(
        self,
        invited_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete invitation

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not invited_id:
            raise ValueError(f"Expected a non-empty value for `invited_id` but received {invited_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/invited/{invited_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncInvitedResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncInvitedResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncInvitedResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncInvitedResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncInvitedResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        group: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> InvitedListResponse:
        """
        Invitations to people to join the group are listed by email

        Args:
          group: filter list by a given group

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/invited/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"group": group}, invited_list_params.InvitedListParams),
            ),
            cast_to=InvitedListResponse,
        )

    async def delete(
        self,
        invited_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete invitation

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not invited_id:
            raise ValueError(f"Expected a non-empty value for `invited_id` but received {invited_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/invited/{invited_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class InvitedResourceWithRawResponse:
    def __init__(self, invited: InvitedResource) -> None:
        self._invited = invited

        self.list = to_raw_response_wrapper(
            invited.list,
        )
        self.delete = to_raw_response_wrapper(
            invited.delete,
        )


class AsyncInvitedResourceWithRawResponse:
    def __init__(self, invited: AsyncInvitedResource) -> None:
        self._invited = invited

        self.list = async_to_raw_response_wrapper(
            invited.list,
        )
        self.delete = async_to_raw_response_wrapper(
            invited.delete,
        )


class InvitedResourceWithStreamingResponse:
    def __init__(self, invited: InvitedResource) -> None:
        self._invited = invited

        self.list = to_streamed_response_wrapper(
            invited.list,
        )
        self.delete = to_streamed_response_wrapper(
            invited.delete,
        )


class AsyncInvitedResourceWithStreamingResponse:
    def __init__(self, invited: AsyncInvitedResource) -> None:
        self._invited = invited

        self.list = async_to_streamed_response_wrapper(
            invited.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            invited.delete,
        )
