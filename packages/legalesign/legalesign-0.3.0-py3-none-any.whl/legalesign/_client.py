# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import (
    pdf,
    user,
    group,
    member,
    signer,
    status,
    invited,
    document,
    template,
    subscribe,
    attachment,
    unsubscribe,
    notifications,
)
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError, LegalesignError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.templatepdf import templatepdf

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Legalesign",
    "AsyncLegalesign",
    "Client",
    "AsyncClient",
]


class Legalesign(SyncAPIClient):
    attachment: attachment.AttachmentResource
    document: document.DocumentResource
    group: group.GroupResource
    invited: invited.InvitedResource
    member: member.MemberResource
    notifications: notifications.NotificationsResource
    pdf: pdf.PdfResource
    signer: signer.SignerResource
    status: status.StatusResource
    subscribe: subscribe.SubscribeResource
    template: template.TemplateResource
    templatepdf: templatepdf.TemplatepdfResource
    unsubscribe: unsubscribe.UnsubscribeResource
    user: user.UserResource
    with_raw_response: LegalesignWithRawResponse
    with_streaming_response: LegalesignWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Legalesign client instance.

        This automatically infers the `api_key` argument from the `LEGALESIGN_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("LEGALESIGN_API_KEY")
        if api_key is None:
            raise LegalesignError(
                "The api_key client option must be set either by passing api_key to the client or by setting the LEGALESIGN_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("LEGALESIGN_BASE_URL")
        if base_url is None:
            base_url = f"https://lon-dev.legalesign.com/api/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.attachment = attachment.AttachmentResource(self)
        self.document = document.DocumentResource(self)
        self.group = group.GroupResource(self)
        self.invited = invited.InvitedResource(self)
        self.member = member.MemberResource(self)
        self.notifications = notifications.NotificationsResource(self)
        self.pdf = pdf.PdfResource(self)
        self.signer = signer.SignerResource(self)
        self.status = status.StatusResource(self)
        self.subscribe = subscribe.SubscribeResource(self)
        self.template = template.TemplateResource(self)
        self.templatepdf = templatepdf.TemplatepdfResource(self)
        self.unsubscribe = unsubscribe.UnsubscribeResource(self)
        self.user = user.UserResource(self)
        self.with_raw_response = LegalesignWithRawResponse(self)
        self.with_streaming_response = LegalesignWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncLegalesign(AsyncAPIClient):
    attachment: attachment.AsyncAttachmentResource
    document: document.AsyncDocumentResource
    group: group.AsyncGroupResource
    invited: invited.AsyncInvitedResource
    member: member.AsyncMemberResource
    notifications: notifications.AsyncNotificationsResource
    pdf: pdf.AsyncPdfResource
    signer: signer.AsyncSignerResource
    status: status.AsyncStatusResource
    subscribe: subscribe.AsyncSubscribeResource
    template: template.AsyncTemplateResource
    templatepdf: templatepdf.AsyncTemplatepdfResource
    unsubscribe: unsubscribe.AsyncUnsubscribeResource
    user: user.AsyncUserResource
    with_raw_response: AsyncLegalesignWithRawResponse
    with_streaming_response: AsyncLegalesignWithStreamedResponse

    # client options
    api_key: str

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncLegalesign client instance.

        This automatically infers the `api_key` argument from the `LEGALESIGN_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("LEGALESIGN_API_KEY")
        if api_key is None:
            raise LegalesignError(
                "The api_key client option must be set either by passing api_key to the client or by setting the LEGALESIGN_API_KEY environment variable"
            )
        self.api_key = api_key

        if base_url is None:
            base_url = os.environ.get("LEGALESIGN_BASE_URL")
        if base_url is None:
            base_url = f"https://lon-dev.legalesign.com/api/v1"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.attachment = attachment.AsyncAttachmentResource(self)
        self.document = document.AsyncDocumentResource(self)
        self.group = group.AsyncGroupResource(self)
        self.invited = invited.AsyncInvitedResource(self)
        self.member = member.AsyncMemberResource(self)
        self.notifications = notifications.AsyncNotificationsResource(self)
        self.pdf = pdf.AsyncPdfResource(self)
        self.signer = signer.AsyncSignerResource(self)
        self.status = status.AsyncStatusResource(self)
        self.subscribe = subscribe.AsyncSubscribeResource(self)
        self.template = template.AsyncTemplateResource(self)
        self.templatepdf = templatepdf.AsyncTemplatepdfResource(self)
        self.unsubscribe = unsubscribe.AsyncUnsubscribeResource(self)
        self.user = user.AsyncUserResource(self)
        self.with_raw_response = AsyncLegalesignWithRawResponse(self)
        self.with_streaming_response = AsyncLegalesignWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        api_key = self.api_key
        return {"Authorization": api_key}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class LegalesignWithRawResponse:
    def __init__(self, client: Legalesign) -> None:
        self.attachment = attachment.AttachmentResourceWithRawResponse(client.attachment)
        self.document = document.DocumentResourceWithRawResponse(client.document)
        self.group = group.GroupResourceWithRawResponse(client.group)
        self.invited = invited.InvitedResourceWithRawResponse(client.invited)
        self.member = member.MemberResourceWithRawResponse(client.member)
        self.notifications = notifications.NotificationsResourceWithRawResponse(client.notifications)
        self.pdf = pdf.PdfResourceWithRawResponse(client.pdf)
        self.signer = signer.SignerResourceWithRawResponse(client.signer)
        self.status = status.StatusResourceWithRawResponse(client.status)
        self.subscribe = subscribe.SubscribeResourceWithRawResponse(client.subscribe)
        self.template = template.TemplateResourceWithRawResponse(client.template)
        self.templatepdf = templatepdf.TemplatepdfResourceWithRawResponse(client.templatepdf)
        self.unsubscribe = unsubscribe.UnsubscribeResourceWithRawResponse(client.unsubscribe)
        self.user = user.UserResourceWithRawResponse(client.user)


class AsyncLegalesignWithRawResponse:
    def __init__(self, client: AsyncLegalesign) -> None:
        self.attachment = attachment.AsyncAttachmentResourceWithRawResponse(client.attachment)
        self.document = document.AsyncDocumentResourceWithRawResponse(client.document)
        self.group = group.AsyncGroupResourceWithRawResponse(client.group)
        self.invited = invited.AsyncInvitedResourceWithRawResponse(client.invited)
        self.member = member.AsyncMemberResourceWithRawResponse(client.member)
        self.notifications = notifications.AsyncNotificationsResourceWithRawResponse(client.notifications)
        self.pdf = pdf.AsyncPdfResourceWithRawResponse(client.pdf)
        self.signer = signer.AsyncSignerResourceWithRawResponse(client.signer)
        self.status = status.AsyncStatusResourceWithRawResponse(client.status)
        self.subscribe = subscribe.AsyncSubscribeResourceWithRawResponse(client.subscribe)
        self.template = template.AsyncTemplateResourceWithRawResponse(client.template)
        self.templatepdf = templatepdf.AsyncTemplatepdfResourceWithRawResponse(client.templatepdf)
        self.unsubscribe = unsubscribe.AsyncUnsubscribeResourceWithRawResponse(client.unsubscribe)
        self.user = user.AsyncUserResourceWithRawResponse(client.user)


class LegalesignWithStreamedResponse:
    def __init__(self, client: Legalesign) -> None:
        self.attachment = attachment.AttachmentResourceWithStreamingResponse(client.attachment)
        self.document = document.DocumentResourceWithStreamingResponse(client.document)
        self.group = group.GroupResourceWithStreamingResponse(client.group)
        self.invited = invited.InvitedResourceWithStreamingResponse(client.invited)
        self.member = member.MemberResourceWithStreamingResponse(client.member)
        self.notifications = notifications.NotificationsResourceWithStreamingResponse(client.notifications)
        self.pdf = pdf.PdfResourceWithStreamingResponse(client.pdf)
        self.signer = signer.SignerResourceWithStreamingResponse(client.signer)
        self.status = status.StatusResourceWithStreamingResponse(client.status)
        self.subscribe = subscribe.SubscribeResourceWithStreamingResponse(client.subscribe)
        self.template = template.TemplateResourceWithStreamingResponse(client.template)
        self.templatepdf = templatepdf.TemplatepdfResourceWithStreamingResponse(client.templatepdf)
        self.unsubscribe = unsubscribe.UnsubscribeResourceWithStreamingResponse(client.unsubscribe)
        self.user = user.UserResourceWithStreamingResponse(client.user)


class AsyncLegalesignWithStreamedResponse:
    def __init__(self, client: AsyncLegalesign) -> None:
        self.attachment = attachment.AsyncAttachmentResourceWithStreamingResponse(client.attachment)
        self.document = document.AsyncDocumentResourceWithStreamingResponse(client.document)
        self.group = group.AsyncGroupResourceWithStreamingResponse(client.group)
        self.invited = invited.AsyncInvitedResourceWithStreamingResponse(client.invited)
        self.member = member.AsyncMemberResourceWithStreamingResponse(client.member)
        self.notifications = notifications.AsyncNotificationsResourceWithStreamingResponse(client.notifications)
        self.pdf = pdf.AsyncPdfResourceWithStreamingResponse(client.pdf)
        self.signer = signer.AsyncSignerResourceWithStreamingResponse(client.signer)
        self.status = status.AsyncStatusResourceWithStreamingResponse(client.status)
        self.subscribe = subscribe.AsyncSubscribeResourceWithStreamingResponse(client.subscribe)
        self.template = template.AsyncTemplateResourceWithStreamingResponse(client.template)
        self.templatepdf = templatepdf.AsyncTemplatepdfResourceWithStreamingResponse(client.templatepdf)
        self.unsubscribe = unsubscribe.AsyncUnsubscribeResourceWithStreamingResponse(client.unsubscribe)
        self.user = user.AsyncUserResourceWithStreamingResponse(client.user)


Client = Legalesign

AsyncClient = AsyncLegalesign
