# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .list_meta import ListMeta
from .status_response import StatusResponse

__all__ = ["StatusRetrieveAllResponse"]


class StatusRetrieveAllResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[StatusResponse]] = None
