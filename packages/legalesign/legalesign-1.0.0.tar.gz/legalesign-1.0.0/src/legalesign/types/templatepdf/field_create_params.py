# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable, Optional
from typing_extensions import Literal, Required, TypedDict

from ..pdf_field_validation_enum import PdfFieldValidationEnum

__all__ = ["FieldCreateParams", "Body"]


class FieldCreateParams(TypedDict, total=False):
    body: Required[Iterable[Body]]


class Body(TypedDict, total=False):
    ax: Required[float]
    """% of page width - left vertical: 0 = left page edge, 1 = right page edge"""

    ay: Required[float]
    """% of page height - upper horizontal: 0 = top page edge, 1 = bottom page edge"""

    bx: Required[float]
    """% of page width - right vertical, 0 = left page edge, 1 = right page edge"""

    by: Required[float]
    """% of page height lower horizontal. 0 = top page edge, 1 = bottom page edge"""

    element_type: Required[Literal["signature", "initials", "text", "admin"]]
    """
    Must be one of the following: _ signature - signature field _ initials -
    initials field _ text - signer field (field for signer to complete) _ admin -
    sender field (field to complete by admin user when sending, use pdftext)
    """

    page: Required[int]
    """which page to place field on"""

    signer: Required[int]
    """1-indexed number of signer (witness+100) (approver+200)"""

    align: Optional[Literal[1, 2, 3]]
    """one of the following:

    - 1 - left
    - 2 - middle
    - 3 - right
    """

    fieldorder: Optional[int]
    """Ordering of fields as the signer progresses (top-down by if left blank)"""

    font_name: Literal["", "arial", "courier", "helvetica", "liberation", "verdana"]

    font_size: int

    hide_border: bool

    label: str
    """Help a signer/sender understand what to do with the form field"""

    label_extra: str
    """unused. more label if required"""

    logic_action: Literal[1, 2, 3]
    """
    offers options for more advanced forms 1 = One of a set of field - radio group 2
    = Sum a set of fields 3 = Conditional upon another field
    """

    logic_group: str
    """values to enable a given logic_action in the form"""

    map_to: str
    """custom data for form integrations"""

    optional: bool
    """Set true to allow field to be ignored"""

    options: str
    """Additional values for certain validation types."""

    substantive: bool
    """
    Set if field substantive to contract terms, if so will not let other sign till
    this field completed
    """

    validation: Optional[PdfFieldValidationEnum]
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

    value: str
