# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SignerGetRejectionReasonResponse"]


class SignerGetRejectionReasonResponse(BaseModel):
    reason: Optional[str] = None

    status: Optional[int] = None
