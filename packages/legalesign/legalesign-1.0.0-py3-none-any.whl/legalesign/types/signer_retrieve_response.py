# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel
from .signer_status_enum import SignerStatusEnum

__all__ = ["SignerRetrieveResponse"]


class SignerRetrieveResponse(BaseModel):
    document: Optional[str] = None

    email: Optional[str] = None

    first_name: Optional[str] = None

    has_fields: Optional[bool] = None

    last_name: Optional[str] = None

    order: Optional[int] = None

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
