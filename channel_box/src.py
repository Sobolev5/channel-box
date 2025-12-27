import contextlib
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
from starlette.websockets import WebSocketDisconnect


class Channel:
    """WebSocket channel wrapper.

    Represents a single WebSocket connection with additional metadata,
    such as expiration time and payload encoding type.
    """

    def __init__(
        self,
        websocket: WebSocket,
        expires: int,
        payload_type: str,
    ) -> None:
        """Initialize a WebSocket channel.

        Args:
            websocket (WebSocket): Starlette WebSocket instance.
            expires (int): Channel time-to-live (TTL) in seconds.
            payload_type (str): Payload encoding type.
                Allowed values: ``json``, ``text``, ``bytes``.
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

    async def _send(self, payload: str) -> bool:
        """Send payload to the WebSocket.

        The payload is sent according to the configured payload type.
        If sending fails, the channel is considered disconnected.

        Args:
            payload (str | bytes | dict): Data to send to the client.

        Returns:
            bool: ``True`` if the payload was sent successfully,
            ``False`` if the connection is closed or failed.
        """
        try:
            match self.payload_type:
                case PayloadTypeEnum.JSON.value:
                    await self.websocket.send_json(payload)
                case PayloadTypeEnum.TEXT.value:
                    await self.websocket.send_text(payload)
                case PayloadTypeEnum.BYTES.value:
                    await self.websocket.send_bytes(payload)
                case _:
                    await self.websocket.send(payload)
        except (WebSocketDisconnect, RuntimeError, OSError, Exception):
            return False

        self.last_active = time.time()
        return True

    async def _is_expired(self) -> bool:
        """Check whether the channel has expired.

        Returns:
            bool: ``True`` if the channel TTL has expired,
            otherwise ``False``.
        """
        return (self.expires + int(self.last_active)) < time.time()

    def __repr__(self) -> str:
        """Return a debug-friendly string representation of the channel."""
        return f"{self.__class__.__name__} {self.uuid} {self.payload_type=} {self.expires=}"


class ChannelBox:
    """In-memory WebSocket channel group manager.

    Manages groups of channels, message broadcasting,
    message history, and automatic cleanup of expired channels.
    """

    CHANNEL_GROUPS: dict = {}
    CHANNEL_GROUPS_HISTORY: dict = {}
    HISTORY_SIZE: int = int(os.getenv("CHANNEL_BOX_HISTORY_SIZE", 1_048_576))

    @classmethod
    async def add_channel_to_group(
        cls,
        channel: Channel,
        group_name: str = "default",
    ) -> None:
        """Add a channel to a group.

        Args:
            channel (Channel): Channel instance to add.
            group_name (str): Name of the group.
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
        """Remove a channel from a group.

        Args:
            channel (Channel): Channel instance to remove.
            group_name (str): Name of the group.
        """
        if channel in cls.CHANNEL_GROUPS.get(group_name, {}):
            with contextlib.suppress(Exception):
                del cls.CHANNEL_GROUPS[group_name][channel]

    @classmethod
    async def group_send(
        cls,
        group_name: str = "default",
        payload: dict | str | bytes = {},
        save_history: bool = False,
    ) -> None:
        """Send a payload to all channels in a group.

        Optionally stores the message in the group history.

        Args:
            group_name (str): Target group name.
            payload (dict | str | bytes): Payload to broadcast.
            save_history (bool): Whether to save the message to history.
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

        for channel in list(cls.CHANNEL_GROUPS.get(group_name, {}).keys()):
            is_sent = await channel._send(payload)
            if not is_sent:
                await cls.remove_channel_from_group(channel, group_name)

    @classmethod
    async def get_groups(cls) -> dict:
        """Return all active channel groups.

        Returns:
            dict: Mapping of group names to channel collections.
        """
        return cls.CHANNEL_GROUPS

    @classmethod
    async def flush_groups(cls) -> None:
        """Remove all channels from all groups."""
        cls.CHANNEL_GROUPS = {}

    @classmethod
    async def get_history(
        cls,
        group_name: str = "",
    ) -> dict:
        """Get message history.

        Args:
            group_name (str): Optional group name.
                If provided, returns history only for that group.

        Returns:
            dict: Message history for the specified group
            or all groups if no name is provided.
        """
        return (
            cls.CHANNEL_GROUPS_HISTORY.get(group_name, {})
            if group_name
            else cls.CHANNEL_GROUPS_HISTORY
        )

    @classmethod
    async def flush_history(cls) -> None:
        """Clear message history for all groups."""
        cls.CHANNEL_GROUPS_HISTORY = {}

    @classmethod
    async def clean_expired(cls) -> None:
        """Remove expired channels from all groups.

        Channels are considered expired if their TTL has elapsed.
        Empty groups are automatically removed.
        """
        for group_name in list(cls.CHANNEL_GROUPS.keys()):
            for channel in list(cls.CHANNEL_GROUPS[group_name].keys()):
                if await channel._is_expired():
                    with contextlib.suppress(Exception):
                        del cls.CHANNEL_GROUPS[group_name][channel]

            if not cls.CHANNEL_GROUPS.get(group_name):
                with contextlib.suppress(Exception):
                    del cls.CHANNEL_GROUPS[group_name]
