# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from .permissions_enum import PermissionsEnum

__all__ = ["MemberCreateParams"]


class MemberCreateParams(TypedDict, total=False):
    email: Required[str]

    group: Required[str]

    do_email: bool
    """use legalesign to send email notification to new user"""

    permission: PermissionsEnum
    """Permissions options:

    - 1 - administrator
    - 2 - team docs visible, create & send
    - 3 - team docs visible, send only
    - 4 - no team sent docs visible, send only
    - 5 - no team docs visible, create & send
    - 6 - team docs visible, read only
    """
