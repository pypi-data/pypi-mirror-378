# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel
from .document_status_enum import DocumentStatusEnum

__all__ = ["DocumentRetrieveResponse"]


class DocumentRetrieveResponse(BaseModel):
    archived: Optional[bool] = None

    auto_archive: Optional[bool] = None
    """Send document archive very soon after signing."""

    cc_emails: Optional[str] = None
    """who will be cc'd with sender on email notification when signed"""

    created: Optional[datetime] = None

    do_email: Optional[bool] = None

    download_final: Optional[bool] = None
    """Final PDF is available to download"""

    footer: Optional[str] = None
    """HTML docs - text for footer if used"""

    footer_height: Optional[int] = None
    """HTMl docs - px height of footer if used"""

    group: Optional[str] = None
    """Resource URI of group"""

    has_fields: Optional[bool] = None

    hash_value: Optional[str] = None
    """SHA256 checksum of final doc, use this to validate your final PDF download"""

    header: Optional[str] = None
    """HTML docs - text for header if used"""

    header_height: Optional[int] = None
    """HTMl docs - px height of header if used"""

    modified: Optional[datetime] = None

    name: Optional[str] = None

    pdf_password: Optional[str] = None
    """PDF password if used and if save-able"""

    pdf_password_type: Optional[str] = None
    """how pdf password is retained"""

    pdftext: Optional[str] = None
    """ignore this"""

    redirect: Optional[str] = None
    """url for signer redirect after signing"""

    resource_uri: Optional[str] = None

    return_signer_links: Optional[bool] = None
    """ignore"""

    sign_mouse: Optional[bool] = None
    """legacy"""

    sign_time: Optional[datetime] = None

    sign_type: Optional[bool] = None
    """legacy"""

    sign_upload: Optional[bool] = None
    """legacy"""

    signature_placement: Optional[int] = None
    """legacy"""

    signature_type: Optional[int] = None
    """legacy - always 4"""

    signers: Optional[List[List[str]]] = None
    """nested arrays with signer details"""

    signers_in_order: Optional[bool] = None

    status: Optional[DocumentStatusEnum] = None
    """Document status options:

    - 10 - Initial state, check signer status for sent/unsent
    - 20 - Fields completed
    - 30 - Signed
    - 40 - Removed (before signing)
    - 50 - Rejected
    """

    tag: Optional[str] = None
    """your reference"""

    tag1: Optional[str] = None
    """your reference"""

    tag2: Optional[str] = None
    """your reference"""

    template: Optional[str] = None

    templatepdf: Optional[str] = None

    text: Optional[str] = None

    user: Optional[str] = None
    """Resource URI of user"""

    uuid: Optional[str] = None
    """Object ID alone"""
