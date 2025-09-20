# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["StatusRetrieveAllParams"]


class StatusRetrieveAllParams(TypedDict, total=False):
    filter: str
    """Filter on archived status, default is false"""

    limit: int
    """Length of dataset to return. Use with offset query to iterate through results."""

    offset: int
    """Offset from start of dataset.

    Use with the limit query to iterate through dataset.
    """
