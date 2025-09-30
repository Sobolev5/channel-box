import logging
import sys
import os
import time
import uuid
import datetime
from .utils import (
    PayloadTypeEnum,
    ChannelMessageDC,
)
from starlette.websockets import WebSocket


logger = logging.getLogger(__name__)


class Channel:
    def __init__(
        self,
        websocket: WebSocket,
        expires: int,
        payload_type: str,
    ) -> None:
        """Main websocket channel class.

        Args:
            websocket (WebSocket): Starlette websocket
            expires (int): Channel ttl in seconds
            payload_type (str): encoding of payload (str, bytes, json)

        """
        assert isinstance(websocket, WebSocket)
        assert isinstance(expires, int)
        assert isinstance(payload_type, str) and payload_type in [
            PayloadTypeEnum.JSON.value,
            PayloadTypeEnum.TEXT.value,
            PayloadTypeEnum.BYTES.value,
        ]

        self.websocket = websocket
        self.expires = expires
        self.payload_type = payload_type
        self.uuid = uuid.uuid4()
        self.last_active = time.time()

    async def _send(self, payload: str) -> None:
        match self.payload_type:
            case PayloadTypeEnum.JSON.value:
                try:
                    await self.websocket.send_json(payload)
                except Exception as error:
                    logging.warning(error)
            case PayloadTypeEnum.TEXT.value:
                try:
                    await self.websocket.send_text(payload)
                except Exception as error:
                    logging.warning(error)
            case PayloadTypeEnum.BYTES.value:
                try:
                    await self.websocket.send_bytes(payload)
                except Exception as error:
                    logging.warning(error)
            case _:
                try:
                    await self.websocket.send(payload)
                except Exception as error:
                    logging.warning(error)
        self.last_active = time.time()  # renew last_active time for active connecitons

    async def _is_expired(self) -> bool:
        return (self.expires + int(self.last_active)) < time.time()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.uuid} {self.payload_type=} {self.expires=}"


class ChannelBox:
    CHANNEL_GROUPS: dict = {}
    CHANNEL_GROUPS_HISTORY: dict = {}
    HISTORY_SIZE: int = int(os.getenv("CHANNEL_BOX_HISTORY_SIZE", 1_048_576))

    @classmethod
    async def add_channel_to_group(
        cls,
        channel: Channel,
        group_name: str = "default",
    ) -> None:
        """Add channel to group.

        Args:
            channel (Channel): Instance of Channel class
            group_name (str): Group name

        """
        if group_name not in cls.CHANNEL_GROUPS:
            cls.CHANNEL_GROUPS[group_name] = {}

        if channel not in cls.CHANNEL_GROUPS[group_name]:
            cls.CHANNEL_GROUPS[group_name][channel] = {
                "created_at": datetime.datetime.now(tz=datetime.UTC)
            }

    @classmethod
    async def remove_channel_from_group(
        cls,
        channel: Channel,
        group_name: str,
    ) -> None:
        """Remove channel from group.

        Args:
            channel (Channel): Instance of Channel class
            group_name (str): Group name

        """
        if channel in cls.CHANNEL_GROUPS.get(group_name, {}):
            try:
                del cls.CHANNEL_GROUPS[group_name][channel]
            except KeyError:
                logger.warning(
                    "Channel %s not found in group %s during cleanup",
                    channel,
                    group_name,
                )

    @classmethod
    async def group_send(
        cls,
        group_name: str = "default",
        payload: dict | str | bytes = {},
        save_history: bool = False,
    ) -> None:
        """Send payload to all channels connected to group.

        Args:
            group_name (str, optional): Group name
            payload (dict, optional): Payload to channel
            save_history (bool, optional): Save message history. Defaults to False.

        """
        if save_history:
            if group_name not in cls.CHANNEL_GROUPS_HISTORY:
                cls.CHANNEL_GROUPS_HISTORY[group_name] = []

            cls.CHANNEL_GROUPS_HISTORY[group_name].append(
                ChannelMessageDC(
                    payload=payload,
                )
            )

            if sys.getsizeof(cls.CHANNEL_GROUPS_HISTORY[group_name]) > cls.HISTORY_SIZE:
                cls.CHANNEL_GROUPS_HISTORY[group_name] = []

        for channel in cls.CHANNEL_GROUPS.get(group_name, {}):
            await channel._send(payload)

    @classmethod
    async def get_groups(
        cls,
    ) -> dict:
        return cls.CHANNEL_GROUPS

    @classmethod
    async def flush_groups(
        cls,
    ) -> None:
        cls.CHANNEL_GROUPS = {}

    @classmethod
    async def get_history(
        cls,
        group_name: str = "",
    ) -> dict:
        return (
            cls.CHANNEL_GROUPS_HISTORY.get(group_name, {})
            if group_name
            else cls.CHANNEL_GROUPS_HISTORY
        )

    @classmethod
    async def flush_history(
        cls,
    ) -> None:
        cls.CHANNEL_GROUPS_HISTORY = {}

    @classmethod
    async def clean_expired(
        cls,
    ) -> None:
        for group_name in cls.CHANNEL_GROUPS:
            for channel in cls.CHANNEL_GROUPS.get(group_name, {}):
                is_expired = await channel._is_expired()
                if is_expired:
                    try:
                        del cls.CHANNEL_GROUPS[group_name][channel]
                    except KeyError:
                        logger.warning(
                            "Channel %s not found in group %s during cleanup",
                            channel,
                            group_name,
                        )

            if not any(cls.CHANNEL_GROUPS.get(group_name, {})):
                try:
                    del cls.CHANNEL_GROUPS[group_name]
                except KeyError:
                    logger.warning("Group %s not found during cleanup", group_name)
