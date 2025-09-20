# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import TypeAlias

from .._models import BaseModel

__all__ = ["SignerRetrieveFieldsResponse", "SignerRetrieveFieldsResponseItem"]


class SignerRetrieveFieldsResponseItem(BaseModel):
    fieldorder: Optional[int] = None

    label: Optional[str] = None

    label_extra: Optional[str] = None

    state: Optional[bool] = None

    value: Optional[str] = None
    """If the field is a signer file this value will be a short lived download URL"""


SignerRetrieveFieldsResponse: TypeAlias = List[SignerRetrieveFieldsResponseItem]
