# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .webhook_event_filter_enum import WebhookEventFilterEnum

__all__ = ["SubscribeCreateWebhookParams"]


class SubscribeCreateWebhookParams(TypedDict, total=False):
    notify: Required[str]
    """
    The type of callback to receive, value must be all, signed, sent, rejected or
    realtime
    """

    url: Required[str]
    """The URL where you wish to get notified"""

    event_filter: Annotated[WebhookEventFilterEnum, PropertyInfo(alias="eventFilter")]

    group: str
