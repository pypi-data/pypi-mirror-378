# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo
from .webhook_event_filter_enum import WebhookEventFilterEnum

__all__ = ["UnsubscribeDeleteWebhookParams"]


class UnsubscribeDeleteWebhookParams(TypedDict, total=False):
    url: Required[str]
    """URL to remove, it must match any registered callback exactly"""

    event_filter: Annotated[WebhookEventFilterEnum, PropertyInfo(alias="eventFilter")]

    group: int
    """if a group filter is applied refer to it with slug or resource_uri"""
