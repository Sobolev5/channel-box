import time
import uuid
from simple_print.functions import sprint_f
from starlette.endpoints import WebSocketEndpoint


CHANNEL_GROUPS = {}


class Channel:
    def __init__(self, websocket, expires, encoding):
        self.channel_uuid = str(uuid.uuid1())
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.created = time.time()

    async def _send(self, payload):
        websocket = self.websocket
        if self.encoding == "json":
            await websocket.send_json(payload)
        elif self.encoding == "text":
            await websocket.send_text(payload)
        elif self.encoding == "bytes":
            await websocket.send_bytes(payload)
        else:
            await websocket.send(payload)
        self.created = time.time()

    def _is_expired(self):
        return self.expires + int(self.created) < time.time()

    def __repr__(self):
        return f"{self.channel_uuid}"


class ChannelEndpoint(WebSocketEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 60 * 60 * 24  
        self.encoding = "json"
        self.groups = CHANNEL_GROUPS

    async def on_connect(self, websocket, **kwargs):
        await super().on_connect(websocket, **kwargs)
        self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)

    async def on_disconnect(self, websocket, close_code):
        await super().on_disconnect(websocket, close_code)
        await self._remove(self.channel)


    async def _remove(self, channel):
        for group in self.groups:
            if channel in self.groups[group]:
                del self.groups[group][channel]

    async def _validate_name(self, name):
        if name.isidentifier():
            return True
        raise TypeError("Group names must be valid python identifier only alphanumerics and underscores are accepted")

    async def _clean_expired(self):
        for group in self.groups:
            for channel in self.groups.get(group, {}):
                if channel._is_expired():
                    del self.groups[group][channel]

    async def get_or_create(self, group):
        assert await self._validate_name(group), "Invalid group name"
        self.groups.setdefault(group, {})
        self.groups[group][self.channel] = ""
        self.group = group

    async def group_send(self, payload):
        await self._clean_expired()
        for channel in self.groups.get(self.group, {}):
            await channel._send(payload)


async def group_send(group, payload):
    for channel_group in CHANNEL_GROUPS:
        if channel_group == group:
            for channel in CHANNEL_GROUPS.get(group, {}):
                await channel._send(payload)

def groups_show():
    for group in CHANNEL_GROUPS:
        sprint_f(f"\n{group}", "green")
        for channel in CHANNEL_GROUPS.get(group, {}):
            sprint_f(channel, "cyan")
            if channel._is_expired():
                sprint_f("expired", "red")

def groups_flush():
    CHANNEL_GROUPS = {}