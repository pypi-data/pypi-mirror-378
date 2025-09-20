# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel
from .list_meta import ListMeta
from .document_status_enum import DocumentStatusEnum

__all__ = ["DocumentListResponse", "Object"]


class Object(BaseModel):
    archived: Optional[bool] = None

    auto_archive: Optional[bool] = None

    cc_emails: Optional[str] = None

    created: Optional[datetime] = None

    do_email: Optional[bool] = None

    download_final: Optional[bool] = None

    group: Optional[str] = None

    modified: Optional[datetime] = None

    name: Optional[str] = None

    pdftext: Optional[str] = None

    redirect: Optional[str] = None

    resource_uri: Optional[str] = None

    return_signer_links: Optional[bool] = None

    signers: Optional[List[List[str]]] = None
    """nested arrays with signer details"""

    signers_in_order: Optional[Literal[0, 1]] = None

    status: Optional[DocumentStatusEnum] = None
    """Document status options:

    - 10 - Initial state, check signer status for sent/unsent
    - 20 - Fields completed
    - 30 - Signed
    - 40 - Removed (before signing)
    - 50 - Rejected
    """

    tag: Optional[str] = None

    tag1: Optional[str] = None

    tag2: Optional[str] = None

    template: Optional[str] = None

    templatepdf: Optional[str] = None

    text: Optional[str] = None

    user: Optional[str] = None

    uuid: Optional[str] = None


class DocumentListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[Object]] = None
