# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel

__all__ = ["TemplateRetrieveResponse"]


class TemplateRetrieveResponse(BaseModel):
    archive: Optional[bool] = None

    created: Optional[datetime] = None

    group: Optional[str] = None

    has_fields: Optional[bool] = None

    latest_text: Optional[str] = None

    modified: Optional[datetime] = None

    resource_uri: Optional[str] = None

    signee_count: Optional[int] = None

    title: Optional[str] = None

    user: Optional[str] = None

    uuid: Optional[str] = None
