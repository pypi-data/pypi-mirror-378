# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .signer_status_enum import SignerStatusEnum

__all__ = ["StatusResponse"]


class StatusResponse(BaseModel):
    archived: Optional[bool] = None

    download_final: Optional[bool] = None

    resource_uri: Optional[str] = None

    status: Optional[SignerStatusEnum] = None
    """Signer status options:

    - 4 - unsent
    - 5 - scheduled to be sent
    - 10 - sent
    - 15 - email opened
    - 20 - visited
    - 30 - fields complete
    - 35 - fields complete ex signature
    - 39 - waiting for witness to complete
    - 40 - signed
    - 50 - downloaded
    - 60 - rejected
    """

    tag: Optional[str] = None

    tag1: Optional[str] = None

    tag2: Optional[str] = None
