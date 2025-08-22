from datetime import UTC, datetime
from enum import Enum
from dataclasses import dataclass
import uuid
from uuid import UUID


class PayloadTypeEnum(Enum):
    JSON = "json"
    TEXT = "text"
    BYTES = "bytes"


@dataclass
class ChannelMessageDC:
    payload: str | bytes | dict
    uuid: UUID = uuid.uuid4()
    created: datetime = datetime.now(tz=UTC)
