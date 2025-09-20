# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..list_meta import ListMeta
from ..pdf_field_validation_enum import PdfFieldValidationEnum

__all__ = ["FieldListResponse", "Object"]


class Object(BaseModel):
    ax: float
    """left vertical, 0 = left page edge, 1 = right page edge"""

    ay: float
    """upper horizontal, 0 = top page edge, 1 = bottom page edge"""

    bx: float
    """right vertical, 0 = left page edge, 1 = right page edge"""

    by: float
    """lower horizontal. 0 = top page edge, 1 = bottom page edge"""

    element_type: Literal["signature", "initials", "text", "admin"]
    """
    Must be one of the following: _ signature - signature field _ initials -
    initials field _ text - signer field (field for signer to complete) _ admin -
    sender field (field to complete by admin user when sending)
    """

    page: int
    """which page to place field on"""

    signer: Optional[int] = None
    """1-Index number for signer (witness+100) (approver+200). Null if sender field."""

    align: Optional[Literal[1, 2, 3]] = None
    """one of the following:

    - 1 - left
    - 2 - middle
    - 3 - right
    """

    fieldorder: Optional[int] = None
    """order signer progresses through fields, top-down if blank"""

    font_name: Optional[Literal["", "arial", "courier", "helvetica", "liberation", "verdana"]] = None

    font_size: Optional[int] = None

    hide_border: Optional[bool] = None

    label: Optional[str] = None
    """help signer/sender understand what to do"""

    label_extra: Optional[str] = None
    """not in use"""

    logic_action: Optional[Literal[1, 2, 3]] = None
    """
    offers options for more advanced forms 1 = One of a set of field (radio group),
    2 = Sum a set of fields, 3 = Conditional upon another field
    """

    logic_group: Optional[str] = None
    """values to enable a given logic_action in the form"""

    map_to: Optional[str] = None
    """custom data for form integrations"""

    optional: Optional[bool] = None

    options: Optional[str] = None
    """user for certain validation types"""

    substantive: Optional[bool] = None
    """
    Set if field substantive to contract terms, if so will not let others sign till
    this field completed
    """

    validation: Optional[PdfFieldValidationEnum] = None
    """fields types and validations:

    - 1 - Email
    - 2 - yyyy/mm/dd
    - 3 - yy/mm/dd
    - 4 - dd/mm/yyyy
    - 5 - dd/mm/yy
    - 6 - mm/dd/yy
    - 7 - mm/dd/yy
    - 8 - yyyy.mm.dd
    - 9 - yy.mm.dd
    - 10 - dd.mm.yyyy
    - 11 - dd.mm.yy
    - 12 - mm.dd.yyyy
    - 13 - mm.dd.yy
    - 14 - yyyy-mm-dd
    - 15 - yy-mm-dd
    - 16 - dd-mm-yyyy
    - 17 - dd-mm-yy
    - 18 - mm-dd-yyyy
    - 19 - mm-dd-yy
    - 20 - Dropdown list, use options attribute for items
    - 24 - Checkbox tick/cross
    - 25 - Checkbox tick/blank
    - 26 - Checkbox cross/blank
    - 30 - yyyy/mm/dd (automatic)
    - 31 - yy/mm/dd (automatic)
    - 32 - dd/yy/yyyy (automatic)
    - 33 - dd/mm/yy (automatic)
    - 34 - mm/dd/yyyy (automatic)
    - 35 - mm/dd/yy (automatic)
    - 36 - yyyy.mm.dd (automatic)
    - 37 - yy.mm.dd (automatic)
    - 38 - dd.mm.yyyy (automatic)
    - 39 - dd.mm.yy (automatic)
    - 40 - mm.dd.yyyy (automatic)
    - 41 - mm.dd.yy (automatic)
    - 42 - yyyy-mm-dd (automatic)
    - 43 - yy-mm-dd (automatic)
    - 44 - dd-mm-yyyy (automatic)
    - 45 - dd-mm-yy (automatic)
    - 46 - mm-dd-yyyy (automatic)
    - 47 - mm-dd-yy (automatic)
    - 48 - d mmmmm yyyy (automatic)
    - 50 - Whole number
    - 51 - Number
    - 52 - Currency (2 decimals)
    - 53 - 1 number
    - 54 - 2 numbers
    - 55 - 3 numbers
    - 56 - 4 numbers
    - 57 - 5 numbers
    - 58 - 6 numbers
    - 59 - 7 numbers
    - 60 - 8 numbers
    - 61 - 9 numbers
    - 62 - 10 numbers
    - 63 - 11 numbers
    - 64 - 12 numbers
    - 65 - 1 characters (any text)
    - 66 - 2 characters (any text)
    - 67 - 3 characters (any text)
    - 68 - 4 characters (any text)
    - 69 - 5 characters (any text)
    - 70 - 6 characters (any text)
    - 71 - 7 characters (any text)
    - 72 - 8 characters (any text)
    - 73 - secret code, add code in options
    - 74 - file attach, append to email to signer
    - 75 - file attach, append to final PDF
    - 76 - file attach, zip with final PDF for internal use, but not signer
    - 77 - force to title caps
    - 78 - force to uppercase
    - 79 - force to lowercase
    - 80 - mm/yy
    - 81 - mm/yyyy
    - 82 - mm.yy
    - 83 - mm.yyyy
    - 84 - mm-yy
    - 85 - mm-yyyy
    - 90 - drawn field
    - 91 - countries list
    - 92 - honorifics list
    """

    value: Optional[str] = None


class FieldListResponse(BaseModel):
    meta: Optional[ListMeta] = None

    objects: Optional[List[Object]] = None
