# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import PermissionsEnum, member_list_params, member_create_params
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
from ..types.member_response import MemberResponse
from ..types.permissions_enum import PermissionsEnum
from ..types.member_list_response import MemberListResponse

__all__ = ["MemberResource", "AsyncMemberResource"]


class MemberResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MemberResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return MemberResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MemberResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return MemberResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        email: str,
        group: str,
        do_email: bool | Omit = omit,
        permission: PermissionsEnum | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        If the email is a registered user then access to group will be immediate,
        otherise an invitation will be created and emailed.

        Args:
          do_email: use legalesign to send email notification to new user

          permission:
              Permissions options:

              - 1 - administrator
              - 2 - team docs visible, create & send
              - 3 - team docs visible, send only
              - 4 - no team sent docs visible, send only
              - 5 - no team docs visible, create & send
              - 6 - team docs visible, read only

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/member/",
            body=maybe_transform(
                {
                    "email": email,
                    "group": group,
                    "do_email": do_email,
                    "permission": permission,
                },
                member_create_params.MemberCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def retrieve(
        self,
        member_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MemberResponse:
        """
        Get group member

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not member_id:
            raise ValueError(f"Expected a non-empty value for `member_id` but received {member_id!r}")
        return self._get(
            f"/member/{member_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemberResponse,
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
    ) -> MemberListResponse:
        """
        List members of groups, one user may be in one or more groups

        Args:
          group: filter list by a given group

          limit: Length of dataset to return. Use with offset query to iterate through results.

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/member/",
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
                    member_list_params.MemberListParams,
                ),
            ),
            cast_to=MemberListResponse,
        )

    def delete(
        self,
        member_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Remove member from group

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not member_id:
            raise ValueError(f"Expected a non-empty value for `member_id` but received {member_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/member/{member_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncMemberResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMemberResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncMemberResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMemberResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncMemberResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        email: str,
        group: str,
        do_email: bool | Omit = omit,
        permission: PermissionsEnum | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        If the email is a registered user then access to group will be immediate,
        otherise an invitation will be created and emailed.

        Args:
          do_email: use legalesign to send email notification to new user

          permission:
              Permissions options:

              - 1 - administrator
              - 2 - team docs visible, create & send
              - 3 - team docs visible, send only
              - 4 - no team sent docs visible, send only
              - 5 - no team docs visible, create & send
              - 6 - team docs visible, read only

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/member/",
            body=await async_maybe_transform(
                {
                    "email": email,
                    "group": group,
                    "do_email": do_email,
                    "permission": permission,
                },
                member_create_params.MemberCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def retrieve(
        self,
        member_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> MemberResponse:
        """
        Get group member

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not member_id:
            raise ValueError(f"Expected a non-empty value for `member_id` but received {member_id!r}")
        return await self._get(
            f"/member/{member_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=MemberResponse,
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
    ) -> MemberListResponse:
        """
        List members of groups, one user may be in one or more groups

        Args:
          group: filter list by a given group

          limit: Length of dataset to return. Use with offset query to iterate through results.

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/member/",
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
                    member_list_params.MemberListParams,
                ),
            ),
            cast_to=MemberListResponse,
        )

    async def delete(
        self,
        member_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Remove member from group

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not member_id:
            raise ValueError(f"Expected a non-empty value for `member_id` but received {member_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/member/{member_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class MemberResourceWithRawResponse:
    def __init__(self, member: MemberResource) -> None:
        self._member = member

        self.create = to_raw_response_wrapper(
            member.create,
        )
        self.retrieve = to_raw_response_wrapper(
            member.retrieve,
        )
        self.list = to_raw_response_wrapper(
            member.list,
        )
        self.delete = to_raw_response_wrapper(
            member.delete,
        )


class AsyncMemberResourceWithRawResponse:
    def __init__(self, member: AsyncMemberResource) -> None:
        self._member = member

        self.create = async_to_raw_response_wrapper(
            member.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            member.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            member.list,
        )
        self.delete = async_to_raw_response_wrapper(
            member.delete,
        )


class MemberResourceWithStreamingResponse:
    def __init__(self, member: MemberResource) -> None:
        self._member = member

        self.create = to_streamed_response_wrapper(
            member.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            member.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            member.list,
        )
        self.delete = to_streamed_response_wrapper(
            member.delete,
        )


class AsyncMemberResourceWithStreamingResponse:
    def __init__(self, member: AsyncMemberResource) -> None:
        self._member = member

        self.create = async_to_streamed_response_wrapper(
            member.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            member.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            member.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            member.delete,
        )
