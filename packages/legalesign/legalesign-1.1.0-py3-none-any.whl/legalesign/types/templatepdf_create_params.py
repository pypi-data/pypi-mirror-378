# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo

__all__ = ["TemplatepdfCreateParams"]


class TemplatepdfCreateParams(TypedDict, total=False):
    group: Required[str]

    pdf_file: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]]
    """base64 encoded PDF file data"""

    archive_upon_send: bool
    """archive PDF when sent"""

    process_tags: bool

    title: str

    user: str
    """assign to group member if not api user"""
