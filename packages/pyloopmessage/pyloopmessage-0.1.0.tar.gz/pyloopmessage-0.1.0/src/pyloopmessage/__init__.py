"""PyLoopMessage: Python client for the LoopMessage iMessage API."""

from .client import LoopMessageClient
from .enums import (
    AlertType,
    AudioFormat,
    DeliveryType,
    MessageEffect,
    MessageStatusEnum,
    MessageType,
    ReactionType,
    ServiceType,
)
from .exceptions import (
    AuthenticationError,
    InsufficientCreditsError,
    InvalidRecipientError,
    LoopMessageError,
    RateLimitError,
)
from .models import (
    GroupInfo,
    LanguageInfo,
    MessageStatus,
    MessageStatusResponse,
    SendMessageResponse,
    SpeechInfo,
    WebhookEvent,
)

__version__ = "0.1.0"
__all__ = [
    "LoopMessageClient",
    "SendMessageResponse",
    "MessageStatus",
    "MessageStatusResponse",
    "GroupInfo",
    "LanguageInfo",
    "SpeechInfo",
    "WebhookEvent",
    "MessageEffect",
    "ReactionType",
    "ServiceType",
    "MessageStatusEnum",
    "AlertType",
    "DeliveryType",
    "MessageType",
    "AudioFormat",
    "LoopMessageError",
    "AuthenticationError",
    "InvalidRecipientError",
    "RateLimitError",
    "InsufficientCreditsError",
]
