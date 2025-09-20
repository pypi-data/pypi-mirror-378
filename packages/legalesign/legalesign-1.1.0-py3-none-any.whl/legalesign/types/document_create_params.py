# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Union, Iterable
from datetime import datetime
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo

__all__ = ["DocumentCreateParams", "Signer", "SignerReviewer"]


class DocumentCreateParams(TypedDict, total=False):
    group: Required[str]

    name: Required[str]

    signers: Required[Iterable[Signer]]

    append_pdf: bool
    """Append Legalesign validation info to final PDF.

    If not included uses the group default.
    """

    auto_archive: bool
    """Send to archive soon after signing. Keeps web app clutter free"""

    cc_emails: str
    """
    Comma delimited string of email addresses that are notified of signing or
    rejection.
    """

    convert_sender_to_signer: bool
    """
    If any sender fields are left blank, convert them to fields for the first
    recipient.
    """

    do_email: bool
    """Use Legalesign email to send notification emails.

    If false suppresses all emails.
    """

    footer: str
    """Text doc only.

    The footer for the final pdf. Use keyword \"default\" to use group default
    footer.
    """

    footer_height: int
    """Text based doc only. Pixel height of PDF footer, if used. 1px = 0.025cm"""

    header: str
    """Text based doc only.

    The header for the final pdf. Use keyword \"default\" to use group header
    footer.
    """

    header_height: int
    """Text based doc only. Pixel height of final PDF footer, if used. 1px = 0.025cm"""

    pdf_password: str
    """Set a password.

    Must be ascii encode-able, you must also set signature_type to 4 and choose a
    pdf_password_type.
    """

    pdf_password_type: Literal[1, 2]
    """1 to store password, 2 for to delete from our records upon final signing."""

    pdftext: Dict[str, str]
    """Assign values to PDF sender fields, use field labels as keys.

    Requires unique fields labels. See also strict_fields.
    """

    redirect: str
    """URL to send the signer to after signing (instead of download page).

    Your URL will include query parameters with ID and state information as follows:
    YOUR-URL?signer=[signer_uid]&doc=[doc_id]&group=[group_id]&signer_state=[signer_status]&doc_state=[doc_status]
    """

    reminders: str
    """
    Put 'default' if you wish to use the default reminder schedule in the group (go
    to web app to set default schedule)
    """

    return_signer_links: bool
    """Return document links for signers in the response BODY."""

    signature_type: int
    """Use 4 to get your executed PDF Certified.

    Recommended. Defaults to 1 (uses a sha256 hash for document integrity).
    """

    signers_in_order: bool
    """Notify signers in their order sequence.

    If false all are notified simulataneously.
    """

    signertext: Dict[str, str]
    """
    Add custom placeholders to signer fields, using labels as keys in an object (as
    for pdftext). Relies on unique labelling.
    """

    strict_fields: bool
    """pdftext fails silently for invalid field value, set to true to return an error"""

    tag: str

    tag1: str

    tag2: str

    template: str
    """Resource URI of text template object.

    This call must contain either one of the attributes text, templatepdf, template.
    """

    templatepdf: str
    """Resource URI of templatepdf object.

    This API call must contain either one of the attributes text, templatepdf,
    template.
    """

    text: str
    """Raw html.

    This API call must contain either one of the attributes text, templatepdf,
    template.
    """

    user: str
    """Assign document another user in the group. Defaults to API"""


class SignerReviewer(TypedDict, total=False):
    email: Required[str]

    firstname: str

    include_link: bool
    """include a link to the signing pages enabling a reviewer to signer"""

    lastname: str


class Signer(TypedDict, total=False):
    email: Required[str]

    firstname: Required[str]

    lastname: Required[str]

    attachments: SequenceNotStr[str]
    """List of attachment resource URIs"""

    behalfof: str
    """deprecated, do not use"""

    decide_later: bool
    """
    Add this you want the previous signer or approver to decide who the next person
    should be. Commonly used for witnesses (see \"role\"). If you use this leave all
    other attributes blank. First signer cannot use this attribute.
    """

    expires: Annotated[Union[str, datetime, None], PropertyInfo(format="iso8601")]
    """ISO8601 formed datetime, set to TZ of sender or timezone if used"""

    message: str
    """
    Your personal message for the party, entered in the centre of the group email
    template. Use the name of a saved email template preceeded by a hash symbol to
    use that template. If there is more than one template of the same name it will
    select the one last modified.
    """

    order: int
    """Zero-indexed signer ordering, deprecated.

    Ordering of signers/witnesses/approvers is now the natural order of your signers
    list.
    """

    reviewers: Iterable[SignerReviewer]

    role: Literal["witness", "approver"]
    """If this person is a witness use \"witness\".

    Required where a witness is defined in your PDF. If this person is a normal
    signer, use \"approver\" to switch to an approver role. Witnesses and witnessed
    signers also require \"sms\" (see also \"decide_later\").
    """

    sms: str
    """Use international format number to add SMS verification.

    Required if a witness or a witnessed signer.
    """

    subject: str
    """Subject line for outbound email"""

    timezone: str
    """
    TZ of the signer, must be valid TZ as per timezoneenum (see User for
    timezoneenum details). If blank uses tz of the sender.
    """
