# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["PdfCreatePreviewParams"]


class PdfCreatePreviewParams(TypedDict, total=False):
    group: Required[str]

    is_signature_per_page: Required[int]

    signature_type: Required[int]

    signee_count: Required[int]
    """number of signers"""

    text: Required[str]
    """raw html"""

    footer: str

    footer_height: int

    header: str

    header_height: int

    pdfheader: bool
    """Set to true to use group default"""

    title: str
