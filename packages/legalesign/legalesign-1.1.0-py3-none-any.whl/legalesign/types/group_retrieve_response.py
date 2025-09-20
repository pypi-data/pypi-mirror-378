# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["GroupRetrieveResponse"]


class GroupRetrieveResponse(BaseModel):
    created: Optional[datetime] = None

    default_email: Optional[str] = None

    default_extraemail: Optional[str] = None

    footer: Optional[str] = None
    """html of content"""

    footer_height: Optional[int] = None

    header: Optional[str] = None

    is_active: Optional[bool] = None

    members: Optional[List[str]] = None
    """list of members uris"""

    modified: Optional[datetime] = None

    name: Optional[str] = None

    pagesize: Optional[int] = None

    public_name: Optional[str] = None

    resource_uri: Optional[str] = None

    slug: Optional[str] = None

    user: Optional[str] = None

    xframe_allow: Optional[bool] = None

    xframe_allow_pdf_edit: Optional[bool] = None
