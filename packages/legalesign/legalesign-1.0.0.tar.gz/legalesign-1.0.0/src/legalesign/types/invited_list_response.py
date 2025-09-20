# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel
from .list_meta import ListMeta

__all__ = ["InvitedListResponse", "Object"]


class Object(BaseModel):
    created: Optional[datetime] = None

    email: Optional[str] = None

    group: Optional[str] = None

    resource_uri: Optional[str] = None


class InvitedListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[Object]] = None
