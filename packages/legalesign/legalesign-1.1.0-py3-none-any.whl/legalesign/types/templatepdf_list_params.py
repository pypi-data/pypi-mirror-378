# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["TemplatepdfListParams"]


class TemplatepdfListParams(TypedDict, total=False):
    archive: str

    group: str
    """can be full resource_uri or only id"""

    limit: int
    """Length of dataset to return. Use with offset query to iterate through results."""

    offset: int
    """Offset from start of dataset.

    Use with the limit query to iterate through dataset.
    """
