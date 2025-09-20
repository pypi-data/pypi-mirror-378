# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel
from .list_meta import ListMeta

__all__ = ["GroupListResponse", "Object"]


class Object(BaseModel):
    created: Optional[datetime] = None

    is_active: Optional[bool] = None

    modified: Optional[datetime] = None

    name: Optional[str] = None

    public_name: Optional[str] = None

    resource_uri: Optional[str] = None

    slug: Optional[str] = None

    user: Optional[str] = None

    xframe_allow: Optional[bool] = None

    xframe_allow_pdf_edit: Optional[bool] = None


class GroupListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[Object]] = None
