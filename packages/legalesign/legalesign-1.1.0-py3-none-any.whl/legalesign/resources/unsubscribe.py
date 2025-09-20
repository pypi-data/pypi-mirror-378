# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import WebhookEventFilterEnum, unsubscribe_delete_webhook_params
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
from ..types.webhook_event_filter_enum import WebhookEventFilterEnum

__all__ = ["UnsubscribeResource", "AsyncUnsubscribeResource"]


class UnsubscribeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UnsubscribeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return UnsubscribeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UnsubscribeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return UnsubscribeResourceWithStreamingResponse(self)

    def delete_webhook(
        self,
        *,
        url: str,
        event_filter: WebhookEventFilterEnum | Omit = omit,
        group: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete webhook

        Args:
          url: URL to remove, it must match any registered callback exactly

          group: if a group filter is applied refer to it with slug or resource_uri

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/unsubscribe/",
            body=maybe_transform(
                {
                    "url": url,
                    "event_filter": event_filter,
                    "group": group,
                },
                unsubscribe_delete_webhook_params.UnsubscribeDeleteWebhookParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncUnsubscribeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUnsubscribeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUnsubscribeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUnsubscribeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncUnsubscribeResourceWithStreamingResponse(self)

    async def delete_webhook(
        self,
        *,
        url: str,
        event_filter: WebhookEventFilterEnum | Omit = omit,
        group: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete webhook

        Args:
          url: URL to remove, it must match any registered callback exactly

          group: if a group filter is applied refer to it with slug or resource_uri

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/unsubscribe/",
            body=await async_maybe_transform(
                {
                    "url": url,
                    "event_filter": event_filter,
                    "group": group,
                },
                unsubscribe_delete_webhook_params.UnsubscribeDeleteWebhookParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class UnsubscribeResourceWithRawResponse:
    def __init__(self, unsubscribe: UnsubscribeResource) -> None:
        self._unsubscribe = unsubscribe

        self.delete_webhook = to_raw_response_wrapper(
            unsubscribe.delete_webhook,
        )


class AsyncUnsubscribeResourceWithRawResponse:
    def __init__(self, unsubscribe: AsyncUnsubscribeResource) -> None:
        self._unsubscribe = unsubscribe

        self.delete_webhook = async_to_raw_response_wrapper(
            unsubscribe.delete_webhook,
        )


class UnsubscribeResourceWithStreamingResponse:
    def __init__(self, unsubscribe: UnsubscribeResource) -> None:
        self._unsubscribe = unsubscribe

        self.delete_webhook = to_streamed_response_wrapper(
            unsubscribe.delete_webhook,
        )


class AsyncUnsubscribeResourceWithStreamingResponse:
    def __init__(self, unsubscribe: AsyncUnsubscribeResource) -> None:
        self._unsubscribe = unsubscribe

        self.delete_webhook = async_to_streamed_response_wrapper(
            unsubscribe.delete_webhook,
        )
