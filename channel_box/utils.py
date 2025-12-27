from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from uuid import UUID, uuid4


class PayloadTypeEnum(Enum):
    """Supported payload encoding types for WebSocket channels."""

    JSON = "json"
    TEXT = "text"
    BYTES = "bytes"


@dataclass(slots=True)
class ChannelMessageDC:
    """Data container for a channel message.

    Stores the payload and metadata used for message history tracking.
    """

    payload: str | bytes | dict
    uuid: UUID = field(default_factory=uuid4)
    created: datetime = field(default_factory=lambda: datetime.now(tz=UTC))
