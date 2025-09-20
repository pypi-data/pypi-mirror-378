# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .list_meta import ListMeta
from .member_response import MemberResponse

__all__ = ["MemberListResponse"]


class MemberListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[MemberResponse]] = None
