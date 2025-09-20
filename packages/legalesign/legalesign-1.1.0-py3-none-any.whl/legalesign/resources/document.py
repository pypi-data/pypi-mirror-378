# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from datetime import datetime
from typing_extensions import Literal

import httpx

from ..types import document_list_params, document_create_params, document_preview_params
from .._types import Body, Omit, Query, Headers, NoneType, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.document_list_response import DocumentListResponse
from ..types.document_create_response import DocumentCreateResponse
from ..types.document_retrieve_response import DocumentRetrieveResponse
from ..types.document_get_fields_response import DocumentGetFieldsResponse

__all__ = ["DocumentResource", "AsyncDocumentResource"]


class DocumentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DocumentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return DocumentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DocumentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return DocumentResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        group: str,
        name: str,
        signers: Iterable[document_create_params.Signer],
        append_pdf: bool | Omit = omit,
        auto_archive: bool | Omit = omit,
        cc_emails: str | Omit = omit,
        convert_sender_to_signer: bool | Omit = omit,
        do_email: bool | Omit = omit,
        footer: str | Omit = omit,
        footer_height: int | Omit = omit,
        header: str | Omit = omit,
        header_height: int | Omit = omit,
        pdf_password: str | Omit = omit,
        pdf_password_type: Literal[1, 2] | Omit = omit,
        pdftext: Dict[str, str] | Omit = omit,
        redirect: str | Omit = omit,
        reminders: str | Omit = omit,
        return_signer_links: bool | Omit = omit,
        signature_type: int | Omit = omit,
        signers_in_order: bool | Omit = omit,
        signertext: Dict[str, str] | Omit = omit,
        strict_fields: bool | Omit = omit,
        tag: str | Omit = omit,
        tag1: str | Omit = omit,
        tag2: str | Omit = omit,
        template: str | Omit = omit,
        templatepdf: str | Omit = omit,
        text: str | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentCreateResponse:
        """
        Create signing document

        Args:
          append_pdf: Append Legalesign validation info to final PDF. If not included uses the group
              default.

          auto_archive: Send to archive soon after signing. Keeps web app clutter free

          cc_emails: Comma delimited string of email addresses that are notified of signing or
              rejection.

          convert_sender_to_signer: If any sender fields are left blank, convert them to fields for the first
              recipient.

          do_email: Use Legalesign email to send notification emails. If false suppresses all
              emails.

          footer: Text doc only. The footer for the final pdf. Use keyword \"default\" to use
              group default footer.

          footer_height: Text based doc only. Pixel height of PDF footer, if used. 1px = 0.025cm

          header: Text based doc only. The header for the final pdf. Use keyword \"default\" to
              use group header footer.

          header_height: Text based doc only. Pixel height of final PDF footer, if used. 1px = 0.025cm

          pdf_password: Set a password. Must be ascii encode-able, you must also set signature_type to 4
              and choose a pdf_password_type.

          pdf_password_type: 1 to store password, 2 for to delete from our records upon final signing.

          pdftext: Assign values to PDF sender fields, use field labels as keys. Requires unique
              fields labels. See also strict_fields.

          redirect: URL to send the signer to after signing (instead of download page). Your URL
              will include query parameters with ID and state information as follows:
              YOUR-URL?signer=[signer_uid]&doc=[doc_id]&group=[group_id]&signer_state=[signer_status]&doc_state=[doc_status]

          reminders: Put 'default' if you wish to use the default reminder schedule in the group (go
              to web app to set default schedule)

          return_signer_links: Return document links for signers in the response BODY.

          signature_type: Use 4 to get your executed PDF Certified. Recommended. Defaults to 1 (uses a
              sha256 hash for document integrity).

          signers_in_order: Notify signers in their order sequence. If false all are notified
              simulataneously.

          signertext: Add custom placeholders to signer fields, using labels as keys in an object (as
              for pdftext). Relies on unique labelling.

          strict_fields: pdftext fails silently for invalid field value, set to true to return an error

          template: Resource URI of text template object. This call must contain either one of the
              attributes text, templatepdf, template.

          templatepdf: Resource URI of templatepdf object. This API call must contain either one of the
              attributes text, templatepdf, template.

          text: Raw html. This API call must contain either one of the attributes text,
              templatepdf, template.

          user: Assign document another user in the group. Defaults to API

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/document/",
            body=maybe_transform(
                {
                    "group": group,
                    "name": name,
                    "signers": signers,
                    "append_pdf": append_pdf,
                    "auto_archive": auto_archive,
                    "cc_emails": cc_emails,
                    "convert_sender_to_signer": convert_sender_to_signer,
                    "do_email": do_email,
                    "footer": footer,
                    "footer_height": footer_height,
                    "header": header,
                    "header_height": header_height,
                    "pdf_password": pdf_password,
                    "pdf_password_type": pdf_password_type,
                    "pdftext": pdftext,
                    "redirect": redirect,
                    "reminders": reminders,
                    "return_signer_links": return_signer_links,
                    "signature_type": signature_type,
                    "signers_in_order": signers_in_order,
                    "signertext": signertext,
                    "strict_fields": strict_fields,
                    "tag": tag,
                    "tag1": tag1,
                    "tag2": tag2,
                    "template": template,
                    "templatepdf": templatepdf,
                    "text": text,
                    "user": user,
                },
                document_create_params.DocumentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentCreateResponse,
        )

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
    ) -> DocumentRetrieveResponse:
        """
        Get document

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._get(
            f"/document/{doc_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentRetrieveResponse,
        )

    def list(
        self,
        *,
        group: str,
        archived: str | Omit = omit,
        created_gt: Union[str, datetime] | Omit = omit,
        email: str | Omit = omit,
        limit: int | Omit = omit,
        modified_gt: Union[str, datetime] | Omit = omit,
        nosigners: str | Omit = omit,
        offset: int | Omit = omit,
        status: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentListResponse:
        """List (unarchived) signing documents.

        Use /status/ if you need high-level
        information.

        Args:
          group: Filter by a specific group, required.

          archived: Filter on archived status, default is false

          created_gt: Filter for those documents created after a certain time

          email: Filter by signer email

          limit: Length of dataset to return. Use with offset query to iterate through results.

          modified_gt: Filter for those documents modified after a certain time

          nosigners: Add value '1' to remove signers information for a faster query

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          status: Filter on document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/document/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "group": group,
                        "archived": archived,
                        "created_gt": created_gt,
                        "email": email,
                        "limit": limit,
                        "modified_gt": modified_gt,
                        "nosigners": nosigners,
                        "offset": offset,
                        "status": status,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            cast_to=DocumentListResponse,
        )

    def archive(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete does not remove permanently but sets it with status 40 (removed) and
        archives it.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/document/{doc_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def delete_permanently(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Permanently deletes data and files.

        You must enable group automated deletion. We
        recommend archiveDocument.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/document/{doc_id}/delete/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def download_audit_log(
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
        Download pdf of audit log

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
            f"/document/{doc_id}/auditlog/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def get_fields(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentGetFieldsResponse:
        """
        Get document fields

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return self._get(
            f"/document/{doc_id}/fields/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetFieldsResponse,
        )

    def preview(
        self,
        *,
        group: str | Omit = omit,
        signee_count: int | Omit = omit,
        text: str | Omit = omit,
        title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Returns a redirect response (302) with link in the Location header to a one-use
        temporary URL you can redirect to, to see a preview of the signing page. Follow
        the redirect immediately since it expires after a few seconds.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            "/document/preview/",
            body=maybe_transform(
                {
                    "group": group,
                    "signee_count": signee_count,
                    "text": text,
                    "title": title,
                },
                document_preview_params.DocumentPreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncDocumentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDocumentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDocumentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDocumentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/legalesign/legalesign-rest-python#with_streaming_response
        """
        return AsyncDocumentResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        group: str,
        name: str,
        signers: Iterable[document_create_params.Signer],
        append_pdf: bool | Omit = omit,
        auto_archive: bool | Omit = omit,
        cc_emails: str | Omit = omit,
        convert_sender_to_signer: bool | Omit = omit,
        do_email: bool | Omit = omit,
        footer: str | Omit = omit,
        footer_height: int | Omit = omit,
        header: str | Omit = omit,
        header_height: int | Omit = omit,
        pdf_password: str | Omit = omit,
        pdf_password_type: Literal[1, 2] | Omit = omit,
        pdftext: Dict[str, str] | Omit = omit,
        redirect: str | Omit = omit,
        reminders: str | Omit = omit,
        return_signer_links: bool | Omit = omit,
        signature_type: int | Omit = omit,
        signers_in_order: bool | Omit = omit,
        signertext: Dict[str, str] | Omit = omit,
        strict_fields: bool | Omit = omit,
        tag: str | Omit = omit,
        tag1: str | Omit = omit,
        tag2: str | Omit = omit,
        template: str | Omit = omit,
        templatepdf: str | Omit = omit,
        text: str | Omit = omit,
        user: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentCreateResponse:
        """
        Create signing document

        Args:
          append_pdf: Append Legalesign validation info to final PDF. If not included uses the group
              default.

          auto_archive: Send to archive soon after signing. Keeps web app clutter free

          cc_emails: Comma delimited string of email addresses that are notified of signing or
              rejection.

          convert_sender_to_signer: If any sender fields are left blank, convert them to fields for the first
              recipient.

          do_email: Use Legalesign email to send notification emails. If false suppresses all
              emails.

          footer: Text doc only. The footer for the final pdf. Use keyword \"default\" to use
              group default footer.

          footer_height: Text based doc only. Pixel height of PDF footer, if used. 1px = 0.025cm

          header: Text based doc only. The header for the final pdf. Use keyword \"default\" to
              use group header footer.

          header_height: Text based doc only. Pixel height of final PDF footer, if used. 1px = 0.025cm

          pdf_password: Set a password. Must be ascii encode-able, you must also set signature_type to 4
              and choose a pdf_password_type.

          pdf_password_type: 1 to store password, 2 for to delete from our records upon final signing.

          pdftext: Assign values to PDF sender fields, use field labels as keys. Requires unique
              fields labels. See also strict_fields.

          redirect: URL to send the signer to after signing (instead of download page). Your URL
              will include query parameters with ID and state information as follows:
              YOUR-URL?signer=[signer_uid]&doc=[doc_id]&group=[group_id]&signer_state=[signer_status]&doc_state=[doc_status]

          reminders: Put 'default' if you wish to use the default reminder schedule in the group (go
              to web app to set default schedule)

          return_signer_links: Return document links for signers in the response BODY.

          signature_type: Use 4 to get your executed PDF Certified. Recommended. Defaults to 1 (uses a
              sha256 hash for document integrity).

          signers_in_order: Notify signers in their order sequence. If false all are notified
              simulataneously.

          signertext: Add custom placeholders to signer fields, using labels as keys in an object (as
              for pdftext). Relies on unique labelling.

          strict_fields: pdftext fails silently for invalid field value, set to true to return an error

          template: Resource URI of text template object. This call must contain either one of the
              attributes text, templatepdf, template.

          templatepdf: Resource URI of templatepdf object. This API call must contain either one of the
              attributes text, templatepdf, template.

          text: Raw html. This API call must contain either one of the attributes text,
              templatepdf, template.

          user: Assign document another user in the group. Defaults to API

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/document/",
            body=await async_maybe_transform(
                {
                    "group": group,
                    "name": name,
                    "signers": signers,
                    "append_pdf": append_pdf,
                    "auto_archive": auto_archive,
                    "cc_emails": cc_emails,
                    "convert_sender_to_signer": convert_sender_to_signer,
                    "do_email": do_email,
                    "footer": footer,
                    "footer_height": footer_height,
                    "header": header,
                    "header_height": header_height,
                    "pdf_password": pdf_password,
                    "pdf_password_type": pdf_password_type,
                    "pdftext": pdftext,
                    "redirect": redirect,
                    "reminders": reminders,
                    "return_signer_links": return_signer_links,
                    "signature_type": signature_type,
                    "signers_in_order": signers_in_order,
                    "signertext": signertext,
                    "strict_fields": strict_fields,
                    "tag": tag,
                    "tag1": tag1,
                    "tag2": tag2,
                    "template": template,
                    "templatepdf": templatepdf,
                    "text": text,
                    "user": user,
                },
                document_create_params.DocumentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentCreateResponse,
        )

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
    ) -> DocumentRetrieveResponse:
        """
        Get document

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._get(
            f"/document/{doc_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentRetrieveResponse,
        )

    async def list(
        self,
        *,
        group: str,
        archived: str | Omit = omit,
        created_gt: Union[str, datetime] | Omit = omit,
        email: str | Omit = omit,
        limit: int | Omit = omit,
        modified_gt: Union[str, datetime] | Omit = omit,
        nosigners: str | Omit = omit,
        offset: int | Omit = omit,
        status: int | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentListResponse:
        """List (unarchived) signing documents.

        Use /status/ if you need high-level
        information.

        Args:
          group: Filter by a specific group, required.

          archived: Filter on archived status, default is false

          created_gt: Filter for those documents created after a certain time

          email: Filter by signer email

          limit: Length of dataset to return. Use with offset query to iterate through results.

          modified_gt: Filter for those documents modified after a certain time

          nosigners: Add value '1' to remove signers information for a faster query

          offset: Offset from start of dataset. Use with the limit query to iterate through
              dataset.

          status: Filter on document status

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/document/",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "group": group,
                        "archived": archived,
                        "created_gt": created_gt,
                        "email": email,
                        "limit": limit,
                        "modified_gt": modified_gt,
                        "nosigners": nosigners,
                        "offset": offset,
                        "status": status,
                    },
                    document_list_params.DocumentListParams,
                ),
            ),
            cast_to=DocumentListResponse,
        )

    async def archive(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Delete does not remove permanently but sets it with status 40 (removed) and
        archives it.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/document/{doc_id}/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def delete_permanently(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """Permanently deletes data and files.

        You must enable group automated deletion. We
        recommend archiveDocument.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/document/{doc_id}/delete/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def download_audit_log(
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
        Download pdf of audit log

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
            f"/document/{doc_id}/auditlog/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def get_fields(
        self,
        doc_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> DocumentGetFieldsResponse:
        """
        Get document fields

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not doc_id:
            raise ValueError(f"Expected a non-empty value for `doc_id` but received {doc_id!r}")
        return await self._get(
            f"/document/{doc_id}/fields/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DocumentGetFieldsResponse,
        )

    async def preview(
        self,
        *,
        group: str | Omit = omit,
        signee_count: int | Omit = omit,
        text: str | Omit = omit,
        title: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> None:
        """
        Returns a redirect response (302) with link in the Location header to a one-use
        temporary URL you can redirect to, to see a preview of the signing page. Follow
        the redirect immediately since it expires after a few seconds.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            "/document/preview/",
            body=await async_maybe_transform(
                {
                    "group": group,
                    "signee_count": signee_count,
                    "text": text,
                    "title": title,
                },
                document_preview_params.DocumentPreviewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class DocumentResourceWithRawResponse:
    def __init__(self, document: DocumentResource) -> None:
        self._document = document

        self.create = to_raw_response_wrapper(
            document.create,
        )
        self.retrieve = to_raw_response_wrapper(
            document.retrieve,
        )
        self.list = to_raw_response_wrapper(
            document.list,
        )
        self.archive = to_raw_response_wrapper(
            document.archive,
        )
        self.delete_permanently = to_raw_response_wrapper(
            document.delete_permanently,
        )
        self.download_audit_log = to_custom_raw_response_wrapper(
            document.download_audit_log,
            BinaryAPIResponse,
        )
        self.get_fields = to_raw_response_wrapper(
            document.get_fields,
        )
        self.preview = to_raw_response_wrapper(
            document.preview,
        )


class AsyncDocumentResourceWithRawResponse:
    def __init__(self, document: AsyncDocumentResource) -> None:
        self._document = document

        self.create = async_to_raw_response_wrapper(
            document.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            document.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            document.list,
        )
        self.archive = async_to_raw_response_wrapper(
            document.archive,
        )
        self.delete_permanently = async_to_raw_response_wrapper(
            document.delete_permanently,
        )
        self.download_audit_log = async_to_custom_raw_response_wrapper(
            document.download_audit_log,
            AsyncBinaryAPIResponse,
        )
        self.get_fields = async_to_raw_response_wrapper(
            document.get_fields,
        )
        self.preview = async_to_raw_response_wrapper(
            document.preview,
        )


class DocumentResourceWithStreamingResponse:
    def __init__(self, document: DocumentResource) -> None:
        self._document = document

        self.create = to_streamed_response_wrapper(
            document.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            document.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            document.list,
        )
        self.archive = to_streamed_response_wrapper(
            document.archive,
        )
        self.delete_permanently = to_streamed_response_wrapper(
            document.delete_permanently,
        )
        self.download_audit_log = to_custom_streamed_response_wrapper(
            document.download_audit_log,
            StreamedBinaryAPIResponse,
        )
        self.get_fields = to_streamed_response_wrapper(
            document.get_fields,
        )
        self.preview = to_streamed_response_wrapper(
            document.preview,
        )


class AsyncDocumentResourceWithStreamingResponse:
    def __init__(self, document: AsyncDocumentResource) -> None:
        self._document = document

        self.create = async_to_streamed_response_wrapper(
            document.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            document.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            document.list,
        )
        self.archive = async_to_streamed_response_wrapper(
            document.archive,
        )
        self.delete_permanently = async_to_streamed_response_wrapper(
            document.delete_permanently,
        )
        self.download_audit_log = async_to_custom_streamed_response_wrapper(
            document.download_audit_log,
            AsyncStreamedBinaryAPIResponse,
        )
        self.get_fields = async_to_streamed_response_wrapper(
            document.get_fields,
        )
        self.preview = async_to_streamed_response_wrapper(
            document.preview,
        )
