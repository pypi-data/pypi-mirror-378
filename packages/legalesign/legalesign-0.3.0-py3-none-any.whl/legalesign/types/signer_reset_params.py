# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["SignerResetParams"]


class SignerResetParams(TypedDict, total=False):
    email: Required[str]
    """Email of signer to revert to."""

    notify: bool
    """Email notify current signer access is being withdrawn"""
