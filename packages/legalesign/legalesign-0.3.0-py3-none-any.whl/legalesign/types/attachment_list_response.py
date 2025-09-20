# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .list_meta import ListMeta
from .attachment_response import AttachmentResponse

__all__ = ["AttachmentListResponse"]


class AttachmentListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[AttachmentResponse]] = None
