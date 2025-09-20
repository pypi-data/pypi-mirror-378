# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

from .timezone_enum import TimezoneEnum

__all__ = ["UserCreateParams"]


class UserCreateParams(TypedDict, total=False):
    email: Required[str]

    first_name: Required[str]

    last_name: Required[str]

    groups: str
    """
    comma delimited list of groups to add user to, can be full group resource_uri or
    groupId
    """

    password: str
    """If not set a verification email is sent.

    Password must be at least 8 chars, include upper and lower case, with a number
    and a special character
    """

    permission: Literal["1", "2", "3", "4", "5", "6"]
    """
    set user permissions _ 1 - admin _ 2 - create and send docs, team user _ 3 -
    readonly, team user _ 4 - send only, team user _ 5 - send only, individual user
    _ 6 - create and send docs, invidual user
    """

    timezone: TimezoneEnum
    """List of available timezones"""
