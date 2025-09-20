# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime

from .._models import BaseModel
from .timezone_enum import TimezoneEnum

__all__ = ["UserRetrieveResponse"]


class UserRetrieveResponse(BaseModel):
    date_joined: Optional[datetime] = None

    email: Optional[str] = None

    first_name: Optional[str] = None

    groups: Optional[List[str]] = None

    last_login: Optional[datetime] = None

    last_name: Optional[str] = None

    resource_uri: Optional[str] = None

    timezone: Optional[TimezoneEnum] = None
    """List of available timezones"""

    username: Optional[str] = None
