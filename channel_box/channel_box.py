import datetime
import sys
import time
import shortuuid
from starlette.endpoints import WebSocketEndpoint


class ChannelBox:

    def __init__(self, HISTORY_SIZE:int=1_048_576):
        # TODO HISTORY_SIZE ENV
        self.created = time.time()
        self.HISTORY_SIZE = HISTORY_SIZE

    _CHANNELS = {}
    _CHANNELS_HISTORY = {}

    async def channel_send(self, channel_name:str="", payload:dict={}, history:bool=False, **kwargs) -> None:

        if history:
            self._CHANNELS_HISTORY.setdefault(channel_name, [])
            self._CHANNELS_HISTORY[channel_name].append({"payload": payload, "uuid": shortuuid.uuid(), "datetime": datetime.datetime.now()})
            if sys.getsizeof(self._CHANNELS_HISTORY[channel_name]) > self.HISTORY_SIZE:  
                self._CHANNELS_HISTORY[channel_name] = []

        for channel in self._CHANNELS.get(channel_name, {}):
            await channel.send(payload)


    async def channels(self):
        return self._CHANNELS


    async def channels_flush(self) -> None:
        self._CHANNELS = {}


    async def history(self, channel_name:str="") -> list: 
        return self._CHANNELS_HISTORY.get(channel_name, []) if channel_name else self._CHANNELS_HISTORY
        
     
    async def history_flush(self) -> None:
        self._CHANNELS_HISTORY = {}


    async def _channel_add(self, channel_name, channel):
        self._CHANNELS.setdefault(channel_name, {})
        self._CHANNELS[channel_name][channel] = True


    async def _channel_remove(self, channel_name, channel):
        if channel in self._CHANNELS.get(channel_name, {}):
            del self._CHANNELS[channel_name][channel]
        if not any(self._CHANNELS.get(channel_name, {})):
            try:
                del self._CHANNELS[channel_name]
            except:
                pass
        await self._clean_expired()


    async def _clean_expired(self):  
        for channel_name in list(self._CHANNELS):        
            for channel in self._CHANNELS.get(channel_name, {}):
                _is_expired = await channel._is_expired()
                if _is_expired:
                    del self._CHANNELS[channel_name][channel]
            if not any(self._CHANNELS.get(channel_name, {})):
                try:
                    del self._CHANNELS[channel_name]
                except Exception as e:
                    # TODO rewrite
                    pass


channel_box = ChannelBox()


class Channel:


    def __init__(self, websocket, expires, encoding):
        self.channel_uuid = shortuuid.uuid()
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.created = time.time()


    async def send(self, payload:dict={}):
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


    async def _is_expired(self):
        return self.expires + int(self.created) < time.time()


    def __repr__(self):
        return f"channel uuid={self.channel_uuid} expires={self.expires} encoding={self.encoding}"


class ChannelBoxEndpoint(WebSocketEndpoint):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.expires = 60 * 60 * 24
        self.encoding = "json"
        self.channel_name = None
        self.channel = None
        self.channel_box = channel_box


    async def on_connect(self, websocket, **kwargs):
        await super().on_connect(websocket, **kwargs)
        self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)


    async def on_disconnect(self, websocket, close_code):
        await super().on_disconnect(websocket, close_code)
        await self.channel_box._channel_remove(self.channel_name, self.channel)


    async def channel_send(self, payload:dict={}, show=False, history=False):
        await self.channel_box.channel_send(self.channel_name, payload, show=show, history=history)


    async def channel_get_or_create(self, channel_name, websocket):
        self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)
        validated_name = await self._validate_name(channel_name)
        assert validated_name, "Channel names must be valid python identifier only alphanumerics and underscores are accepted"
        await self.channel_box._channel_add(channel_name, self.channel)
        self.channel_name = channel_name


    async def _validate_name(self, name):       
        if name.isidentifier():
            return True
        else:
            return False
