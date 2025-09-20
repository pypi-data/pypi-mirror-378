# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from datetime import datetime
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DocumentListParams"]


class DocumentListParams(TypedDict, total=False):
    group: Required[str]
    """Filter by a specific group, required."""

    archived: str
    """Filter on archived status, default is false"""

    created_gt: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter for those documents created after a certain time"""

    email: str
    """Filter by signer email"""

    limit: int
    """Length of dataset to return. Use with offset query to iterate through results."""

    modified_gt: Annotated[Union[str, datetime], PropertyInfo(format="iso8601")]
    """Filter for those documents modified after a certain time"""

    nosigners: str
    """Add value '1' to remove signers information for a faster query"""

    offset: int
    """Offset from start of dataset.

    Use with the limit query to iterate through dataset.
    """

    status: int
    """Filter on document status"""
