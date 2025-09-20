# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["AttachmentResponse"]


class AttachmentResponse(BaseModel):
    created: Optional[datetime] = None

    description: Optional[str] = None

    filename: Optional[str] = None

    group: Optional[str] = None

    resource_uri: Optional[str] = None

    user: Optional[str] = None
    """resource_uri for user"""

    uuid: Optional[str] = None
    """id for attachment object"""
