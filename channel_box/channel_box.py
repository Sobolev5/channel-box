import datetime
import sys
import time
import uuid

from simple_print import sprint
from starlette.endpoints import WebSocketEndpoint


DEBUG_CHANNEL_BOX = False


class ChannelBox:
    def __init__(self):
        self.created = time.time()

    _CHANNELS = {}
    _CHANNELS_HISTORY = {}

    created = None

    async def channel_send(self, channel_name, payload, show=False, history=False):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBox :: channel_send channel_name={channel_name} show={show} payload={payload} history={history}", c="green", s=1)

        for channel in self._CHANNELS.get(channel_name, {}):
            await channel.send(payload)

            if history:
                self._CHANNELS_HISTORY.setdefault(channel_name, [])
                self._CHANNELS_HISTORY[channel_name].append({"payload": payload, "datetime": datetime.datetime.now().strftime("%d.%m.%Y %H:%M")})
                if sys.getsizeof(self._CHANNELS_HISTORY[channel_name]) > 104857600:  # 100MB
                    self._CHANNELS_HISTORY[channel_name] = []

            if show:
                sprint(f"Send successfully to channel {channel}", c="blue", s=1, p=1)

        if show and not self._CHANNELS:
            sprint("Channels is empty", c="red", s=1, p=1)

    async def channels_show(self):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBox :: channels_show", c="green", s=1)

        if self._CHANNELS:
            for channel_name, channels in list(self._CHANNELS.items()):
                sprint(f"----- [Channel name] {channel_name}", c="green", s=1, p=1)
                for index, channel in enumerate(channels):
                    if channel:
                        sprint(f"----- [Connection] {index}: {channel}", s=1, p=1)
                        is_expired = await channel.is_expired()
                        if is_expired:
                            sprint("expired", c="red", s=1, p=1)
                        if channel_name in self._CHANNELS_HISTORY:
                            print("----- [Last 100 messages] ", self._CHANNELS_HISTORY[channel_name][::-1])
                print("\n")

        else:
            sprint("Channels is empty", c="red", s=1, p=1)

    async def history_get(self, channel_name):
        history = self._CHANNELS_HISTORY.get(channel_name, [])
        return history

    async def channels_flush(self):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBox :: channels_flush", c="green", s=1)

        self._CHANNELS = {}

    async def _channel_add(self, channel_name, channel):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBox :: _channel_add channel_name={channel_name} channel={channel}", c="green", s=1)

        self._CHANNELS.setdefault(channel_name, {})
        self._CHANNELS[channel_name][channel] = True

    async def _remove_channel(self, channel_name, channel):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBox :: _remove_channel channel_name={channel_name} channel={channel}", c="green", s=1)

        if channel in self._CHANNELS.get(channel_name, {}):
            del self._CHANNELS[channel_name][channel]

        if not any(self._CHANNELS.get(channel_name, {})):
            try:
                del self._CHANNELS[channel_name]
            except:
                pass

        await self._clean_expired()

    async def _clean_expired(self):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBox :: _clean_expired", c="green", s=1)

        for channel_name in list(self._CHANNELS):

            for channel in self._CHANNELS.get(channel_name, {}):
                is_expired = await channel.is_expired()
                if is_expired:
                    del self._CHANNELS[channel_name][channel]

            if not any(self._CHANNELS.get(channel_name, {})):
                try:
                    del self._CHANNELS[channel_name]
                except:
                    pass


channel_box = ChannelBox()


class Channel:
    def __init__(self, websocket, expires, encoding):
        self.channel_uuid = str(uuid.uuid1())
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.created = time.time()

    async def send(self, payload):

        if DEBUG_CHANNEL_BOX:
            sprint(f"Channel :: send payload={payload} webscocket={self.websocket} expires={self.expires} encoding={self.encoding} created={self.created}", c="yellow", s=1)

        websocket = self.websocket
        if self.encoding == "json":
            try:
                await websocket.send_json(payload)
            except RuntimeError:
                pass
        elif self.encoding == "text":
            try:
                await websocket.send_text(payload)
            except RuntimeError:
                pass
        elif self.encoding == "bytes":
            try:
                await websocket.send_bytes(payload)
            except RuntimeError:
                pass
        else:
            try:
                await websocket.send(payload)
            except RuntimeError:
                pass
        self.created = time.time()

    async def is_expired(self):

        if DEBUG_CHANNEL_BOX:
            sprint(f"Channel :: is_expired", c="yellow", s=1)

        return self.expires + int(self.created) < time.time()

    def __repr__(self):
        return f"Channel uuid={self.channel_uuid} expires={self.expires} encoding={self.encoding}"


class ChannelBoxEndpoint(WebSocketEndpoint):
    def __init__(self, *args, **kwargs):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBoxEndpoint :: __init__ args={args} kwargs={kwargs}", c="cyan", s=1)

        super().__init__(*args, **kwargs)
        self.expires = 60 * 60 * 24
        self.encoding = "json"
        self.channel_name = None
        self.channel = None
        self.channel_box = channel_box

    async def on_connect(self, websocket, **kwargs):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBoxEndpoint :: on_connect websocket={websocket}", c="cyan", s=1)

        await super().on_connect(websocket, **kwargs)
        self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)

    async def on_disconnect(self, websocket, close_code):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBoxEndpoint :: on_disconnect websocket={websocket} close_code={close_code}", c="cyan", s=1)

        await super().on_disconnect(websocket, close_code)
        await self.channel_box._remove_channel(self.channel_name, self.channel)

    async def channel_send(self, payload, show=False, history=False):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBoxEndpoint :: channel_send payload={payload}", c="cyan", s=1)

        await self.channel_box.channel_send(self.channel_name, payload, show=show, history=history)

    async def channel_get_or_create(self, channel_name, websocket=None):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBoxEndpoint :: channel_get_or_create channel_name={channel_name} channel={self.channel}", c="cyan", s=1)

        if websocket:
            self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)

        validated_name = await self._validate_name(channel_name)
        assert validated_name, "Channel names must be valid python identifier only alphanumerics and underscores are accepted"
        await self.channel_box._channel_add(channel_name, self.channel)
        self.channel_name = channel_name

    async def _validate_name(self, name):

        if DEBUG_CHANNEL_BOX:
            sprint(f"ChannelBoxEndpoint :: _validate_name name={name}", c="cyan", s=1)

        if name.isidentifier():
            return True
        else:
            return False
