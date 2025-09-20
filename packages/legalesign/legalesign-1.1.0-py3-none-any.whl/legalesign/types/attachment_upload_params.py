# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Required, Annotated, TypedDict

from .._types import Base64FileInput
from .._utils import PropertyInfo

__all__ = ["AttachmentUploadParams"]


class AttachmentUploadParams(TypedDict, total=False):
    filename: Required[str]
    """Simple alphanumeric name ending .pdf"""

    group: Required[str]
    """URI of the group name"""

    pdf_file: Required[Annotated[Union[str, Base64FileInput], PropertyInfo(format="base64")]]
    """Base64 encoded PDF file data, max size is a group setting, 5MB by default"""

    description: str

    user: str
    """Assign to group member if not the api user"""
