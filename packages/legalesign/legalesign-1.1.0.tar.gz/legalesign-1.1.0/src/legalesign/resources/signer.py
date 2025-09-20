# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import signer_reset_params, signer_send_reminder_params
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
from ..types.signer_retrieve_response import SignerRetrieveResponse
from ..types.signer_retrieve_fields_response import SignerRetrieveFieldsResponse
from ..types.signer_get_rejection_reason_response import SignerGetRejectionReasonResponse

__all__ = ["SignerResource", "AsyncSignerResource"]


class SignerResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SignerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return SignerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SignerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return SignerResourceWithStreamingResponse(self)

    def retrieve(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignerRetrieveResponse:
        """
        Get status and details of an individual signer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        return self._get(
            f"/signer/{signer_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignerRetrieveResponse,
        )

    def get_access_link(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Returns 1-use link for signer in Location header.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/signer/{signer_id}/new-link/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def get_rejection_reason(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignerGetRejectionReasonResponse:
        """
        Returns reason signer gave for rejecting a document, if given

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        return self._get(
            f"/signer/{signer_id}/rejection/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignerGetRejectionReasonResponse,
        )

    def reset(
        self,
        signer_id: str,
        *,
        email: str,
        notify: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Reset to an earlier signer if forwarded

        Args:
          email: Email of signer to revert to.

          notify: Email notify current signer access is being withdrawn

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/signer/{signer_id}/reset/",
            body=maybe_transform(
                {
                    "email": email,
                    "notify": notify,
                },
                signer_reset_params.SignerResetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve_fields(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignerRetrieveFieldsResponse:
        """
        Get signer form fields

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        return self._get(
            f"/signer/{signer_id}/fields1/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignerRetrieveFieldsResponse,
        )

    def send_reminder(
        self,
        signer_id: str,
        *,
        text: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Send signer reminder email

        Args:
          text: custom message text, html will be stripped

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/signer/{signer_id}/send-reminder/",
            body=maybe_transform({"text": text}, signer_send_reminder_params.SignerSendReminderParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncSignerResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSignerResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSignerResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSignerResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncSignerResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignerRetrieveResponse:
        """
        Get status and details of an individual signer

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        return await self._get(
            f"/signer/{signer_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignerRetrieveResponse,
        )

    async def get_access_link(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Returns 1-use link for signer in Location header.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/signer/{signer_id}/new-link/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def get_rejection_reason(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignerGetRejectionReasonResponse:
        """
        Returns reason signer gave for rejecting a document, if given

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        return await self._get(
            f"/signer/{signer_id}/rejection/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignerGetRejectionReasonResponse,
        )

    async def reset(
        self,
        signer_id: str,
        *,
        email: str,
        notify: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Reset to an earlier signer if forwarded

        Args:
          email: Email of signer to revert to.

          notify: Email notify current signer access is being withdrawn

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/signer/{signer_id}/reset/",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "notify": notify,
                },
                signer_reset_params.SignerResetParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve_fields(
        self,
        signer_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignerRetrieveFieldsResponse:
        """
        Get signer form fields

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        return await self._get(
            f"/signer/{signer_id}/fields1/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignerRetrieveFieldsResponse,
        )

    async def send_reminder(
        self,
        signer_id: str,
        *,
        text: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Send signer reminder email

        Args:
          text: custom message text, html will be stripped

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not signer_id:
            raise ValueError(f"Expected a non-empty value for `signer_id` but received {signer_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/signer/{signer_id}/send-reminder/",
            body=await async_maybe_transform({"text": text}, signer_send_reminder_params.SignerSendReminderParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class SignerResourceWithRawResponse:
    def __init__(self, signer: SignerResource) -> None:
        self._signer = signer

        self.retrieve = to_raw_response_wrapper(
            signer.retrieve,
        )
        self.get_access_link = to_raw_response_wrapper(
            signer.get_access_link,
        )
        self.get_rejection_reason = to_raw_response_wrapper(
            signer.get_rejection_reason,
        )
        self.reset = to_raw_response_wrapper(
            signer.reset,
        )
        self.retrieve_fields = to_raw_response_wrapper(
            signer.retrieve_fields,
        )
        self.send_reminder = to_raw_response_wrapper(
            signer.send_reminder,
        )


class AsyncSignerResourceWithRawResponse:
    def __init__(self, signer: AsyncSignerResource) -> None:
        self._signer = signer

        self.retrieve = async_to_raw_response_wrapper(
            signer.retrieve,
        )
        self.get_access_link = async_to_raw_response_wrapper(
            signer.get_access_link,
        )
        self.get_rejection_reason = async_to_raw_response_wrapper(
            signer.get_rejection_reason,
        )
        self.reset = async_to_raw_response_wrapper(
            signer.reset,
        )
        self.retrieve_fields = async_to_raw_response_wrapper(
            signer.retrieve_fields,
        )
        self.send_reminder = async_to_raw_response_wrapper(
            signer.send_reminder,
        )


class SignerResourceWithStreamingResponse:
    def __init__(self, signer: SignerResource) -> None:
        self._signer = signer

        self.retrieve = to_streamed_response_wrapper(
            signer.retrieve,
        )
        self.get_access_link = to_streamed_response_wrapper(
            signer.get_access_link,
        )
        self.get_rejection_reason = to_streamed_response_wrapper(
            signer.get_rejection_reason,
        )
        self.reset = to_streamed_response_wrapper(
            signer.reset,
        )
        self.retrieve_fields = to_streamed_response_wrapper(
            signer.retrieve_fields,
        )
        self.send_reminder = to_streamed_response_wrapper(
            signer.send_reminder,
        )


class AsyncSignerResourceWithStreamingResponse:
    def __init__(self, signer: AsyncSignerResource) -> None:
        self._signer = signer

        self.retrieve = async_to_streamed_response_wrapper(
            signer.retrieve,
        )
        self.get_access_link = async_to_streamed_response_wrapper(
            signer.get_access_link,
        )
        self.get_rejection_reason = async_to_streamed_response_wrapper(
            signer.get_rejection_reason,
        )
        self.reset = async_to_streamed_response_wrapper(
            signer.reset,
        )
        self.retrieve_fields = async_to_streamed_response_wrapper(
            signer.retrieve_fields,
        )
        self.send_reminder = async_to_streamed_response_wrapper(
            signer.send_reminder,
        )
