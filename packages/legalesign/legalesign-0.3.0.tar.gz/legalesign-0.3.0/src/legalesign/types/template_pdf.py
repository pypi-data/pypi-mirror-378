# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["TemplatePdf"]


class TemplatePdf(BaseModel):
    created: Optional[datetime] = None

    group: Optional[str] = None

    modified: Optional[datetime] = None

    page_count: Optional[int] = None

    parties: Optional[str] = None
    """JSON stringified array of document parties"""

    resource_uri: Optional[str] = None

    signer_count: Optional[int] = None

    title: Optional[str] = None

    user: Optional[str] = None
    """resource_uri for user"""

    uuid: Optional[str] = None
    """id for pdf object"""

    valid: Optional[bool] = None
    """Is able to be sent (if fields do not validate)"""
