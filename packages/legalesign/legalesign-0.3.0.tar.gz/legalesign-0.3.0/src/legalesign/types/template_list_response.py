# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel
from .list_meta import ListMeta

__all__ = ["TemplateListResponse", "Object"]


class Object(BaseModel):
    archive: Optional[bool] = None

    created: Optional[datetime] = None

    group: Optional[str] = None

    has_fields: Optional[bool] = None

    modified: Optional[datetime] = None

    resource_uri: Optional[str] = None

    signee_count: Optional[int] = None

    title: Optional[str] = None

    user: Optional[str] = None

    uuid: Optional[str] = None


class TemplateListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[Object]] = None
