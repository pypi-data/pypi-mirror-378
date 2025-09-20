# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ListMeta"]


class ListMeta(BaseModel):
    limit: Optional[int] = None

    next: Optional[str] = None

    offset: Optional[int] = None

    previous: Optional[str] = None

    total_count: Optional[int] = None
    """total number of objects"""
