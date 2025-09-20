# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["InvitedListParams"]


class InvitedListParams(TypedDict, total=False):
    group: str
    """filter list by a given group"""
