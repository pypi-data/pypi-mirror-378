# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from .._models import BaseModel
from .permissions_enum import PermissionsEnum

__all__ = ["MemberResponse"]


class MemberResponse(BaseModel):
    created: Optional[datetime] = None

    group: Optional[str] = None

    modified: Optional[datetime] = None

    permission: Optional[PermissionsEnum] = None
    """Permissions options:

    - 1 - administrator
    - 2 - team docs visible, create & send
    - 3 - team docs visible, send only
    - 4 - no team sent docs visible, send only
    - 5 - no team docs visible, create & send
    - 6 - team docs visible, read only
    """

    resource_uri: Optional[str] = None

    user: Optional[str] = None
