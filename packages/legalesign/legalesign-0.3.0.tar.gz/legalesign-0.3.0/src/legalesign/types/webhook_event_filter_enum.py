# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing_extensions import Literal, TypeAlias

__all__ = ["WebhookEventFilterEnum"]

WebhookEventFilterEnum: TypeAlias = Literal[
    "",
    "document.*",
    "document.created",
    "document.rejected",
    "document.finalPdfCreated",
    "recipient.*",
    "recipient.completed",
    "recipient.rejected",
    "recipient.emailOpened",
    "recipient.visiting",
    "recipient.bounced",
]
