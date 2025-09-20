# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import WebhookEventFilterEnum, subscribe_create_webhook_params
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

__all__ = ["SubscribeResource", "AsyncSubscribeResource"]


class SubscribeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SubscribeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return SubscribeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SubscribeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return SubscribeResourceWithStreamingResponse(self)

    def create_webhook(
        self,
        *,
        notify: str,
        url: str,
        event_filter: WebhookEventFilterEnum | Omit = omit,
        group: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Create webhook

        Args:
          notify: The type of callback to receive, value must be all, signed, sent, rejected or
              realtime

          url: The URL where you wish to get notified

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/subscribe/",
            body=maybe_transform(
                {
                    "notify": notify,
                    "url": url,
                    "event_filter": event_filter,
                    "group": group,
                },
                subscribe_create_webhook_params.SubscribeCreateWebhookParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncSubscribeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSubscribeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSubscribeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSubscribeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncSubscribeResourceWithStreamingResponse(self)

    async def create_webhook(
        self,
        *,
        notify: str,
        url: str,
        event_filter: WebhookEventFilterEnum | Omit = omit,
        group: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Create webhook

        Args:
          notify: The type of callback to receive, value must be all, signed, sent, rejected or
              realtime

          url: The URL where you wish to get notified

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/subscribe/",
            body=await async_maybe_transform(
                {
                    "notify": notify,
                    "url": url,
                    "event_filter": event_filter,
                    "group": group,
                },
                subscribe_create_webhook_params.SubscribeCreateWebhookParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SubscribeResourceWithRawResponse:
    def __init__(self, subscribe: SubscribeResource) -> None:
        self._subscribe = subscribe

        self.create_webhook = to_raw_response_wrapper(
            subscribe.create_webhook,
        )


class AsyncSubscribeResourceWithRawResponse:
    def __init__(self, subscribe: AsyncSubscribeResource) -> None:
        self._subscribe = subscribe

        self.create_webhook = async_to_raw_response_wrapper(
            subscribe.create_webhook,
        )


class SubscribeResourceWithStreamingResponse:
    def __init__(self, subscribe: SubscribeResource) -> None:
        self._subscribe = subscribe

        self.create_webhook = to_streamed_response_wrapper(
            subscribe.create_webhook,
        )


class AsyncSubscribeResourceWithStreamingResponse:
    def __init__(self, subscribe: AsyncSubscribeResource) -> None:
        self._subscribe = subscribe

        self.create_webhook = async_to_streamed_response_wrapper(
            subscribe.create_webhook,
        )
