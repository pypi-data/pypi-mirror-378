# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["TemplateCreateParams"]


class TemplateCreateParams(TypedDict, total=False):
    group: Required[str]

    latest_text: Required[str]
    """text/html for template"""

    title: Required[str]

    user: str
    """assign to a user if not api user"""
