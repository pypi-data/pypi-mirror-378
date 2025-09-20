# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["DocumentPreviewParams"]


class DocumentPreviewParams(TypedDict, total=False):
    group: str

    signee_count: int

    text: str

    title: str
