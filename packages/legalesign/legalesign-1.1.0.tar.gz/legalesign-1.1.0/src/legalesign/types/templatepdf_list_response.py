# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel
from .list_meta import ListMeta
from .template_pdf import TemplatePdf

__all__ = ["TemplatepdfListResponse"]


class TemplatepdfListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[TemplatePdf]] = None
