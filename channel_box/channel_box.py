import time
import uuid
from simple_print.functions import sprint_f
from starlette.endpoints import WebSocketEndpoint


class ChannelGroups:

    def __init__(self):
        self.created = time.time()  

    _CHANNEL_GROUPS = {} 
    created = None

    async def group_send(self, group, payload):
        self.clean_expired()
        for channel in self._CHANNEL_GROUPS.get(group, {}):
            await channel.send(payload)

    def groups_show(self):
        if self._CHANNEL_GROUPS:
            for group in self._CHANNEL_GROUPS:
                sprint_f(f"\n{group}", "green")
                for channel in self._CHANNEL_GROUPS.get(group, {}):
                    sprint_f(channel, "cyan")
                    if channel.is_expired():
                        sprint_f("expired", "red")
        else:
            sprint_f("Channel groups is empty", "yellow")    

    def groups_flush(self):
        self._CHANNEL_GROUPS = {}

    def group_add(self, group, channel):
        self._CHANNEL_GROUPS.setdefault(group, {})
        self._CHANNEL_GROUPS[group][channel] = ""

    def remove_channel(self, channel):
        for group in self._CHANNEL_GROUPS:
            if channel in self._CHANNEL_GROUPS[group]:
                del self._CHANNEL_GROUPS[group][channel]
                if not any(self._CHANNEL_GROUPS[group]):
                    del self._CHANNEL_GROUPS[group]            

    def clean_expired(self):
        for group in self._CHANNEL_GROUPS:
            for channel in self._CHANNEL_GROUPS.get(group, {}):
                if channel.is_expired():
                    del self._CHANNEL_GROUPS[group][channel]
                    if not any(self._CHANNEL_GROUPS[group]):
                        del self._CHANNEL_GROUPS[group]            


channel_groups = ChannelGroups()


class Channel:

    def __init__(self, websocket, expires, encoding):
        self.channel_uuid = str(uuid.uuid1())
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.created = time.time()

    async def send(self, payload):
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

    def is_expired(self):
        return self.expires + int(self.created) < time.time()

    def __repr__(self):
        return f"{self.channel_uuid}"


class ChannelEndpoint(WebSocketEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 60 * 60 * 24  
        self.encoding = "json"
        self.channel_groups = channel_groups

    async def on_connect(self, websocket, **kwargs):
        await super().on_connect(websocket, **kwargs)
        self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)

    async def on_disconnect(self, websocket, close_code):
        await super().on_disconnect(websocket, close_code)
        self.channel_groups.remove_channel(self.channel)

    async def group_send(self, payload):
        await self.channel_groups.group_send(self.group, payload)

    def get_or_create(self, group):
        assert self._validate_name(group), "Invalid group name"
        self.channel_groups.group_add(group, self.channel)
        self.group = group

    def _validate_name(self, name):
        if name.isidentifier():
            return True
        raise TypeError("Group names must be valid python identifier only alphanumerics and underscores are accepted")