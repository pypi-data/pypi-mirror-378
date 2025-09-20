# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal, TypeAlias

from .._models import BaseModel
from .webhook_event_filter_enum import WebhookEventFilterEnum

__all__ = ["NotificationListResponse", "NotificationListResponseItem"]


class NotificationListResponseItem(BaseModel):
    active: Optional[bool] = None

    event_filter: Optional[WebhookEventFilterEnum] = None

    group_id: Optional[int] = None

    notify_when: Optional[Literal[1, 2, 3, 4, 10]] = None
    """1 = every 6 minutes, 2 = upon signing, 3 = sent, 4 = rejected, 10 = realtime"""

    url: Optional[str] = None


NotificationListResponse: TypeAlias = List[NotificationListResponseItem]
