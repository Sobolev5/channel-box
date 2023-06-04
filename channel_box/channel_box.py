from __future__ import annotations
import datetime
import sys
import os
import time
import shortuuid
import logging
from enum import Enum
from starlette.websockets import WebSocket
from starlette.endpoints import WebSocketEndpoint


class Channel:
    """ 
    Channel class.

    websocket: WebSocket, Starlette websocket instance (see starlette documentation)
    expires: int, channel ttl in seconds
    encoding: str [json, text, bytes], encoding of sending data
    channel_uuid: str, unique identifier of channnel
    created: time, channel creation time
    """ 
    def __init__(self, websocket: WebSocket, expires: int, encoding: str) -> None:       
        assert isinstance(websocket, WebSocket)
        assert isinstance(expires, int)
        assert isinstance(encoding, int) and encoding in ["json", "text", "bytes"], "Must be in ['json', 'text', 'bytes']"
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.channel_uuid = shortuuid.uuid()
        self.created = time.time()

    async def send(self, payload: dict={}) -> None:
        assert isinstance(payload, dict)
        websocket = self.websocket
        if self.encoding == "json":
            try:
                await websocket.send_json(payload)
            except RuntimeError as error:
                logging.debug(error)  
        elif self.encoding == "text":
            try:
                await websocket.send_text(payload)
            except RuntimeError as error:
                logging.debug(error)  
        elif self.encoding == "bytes":
            try:
                await websocket.send_bytes(payload)
            except RuntimeError as error:
                logging.debug(error)  
        else:
            try:
                await websocket.send(payload)
            except RuntimeError as error:
                logging.debug(error)  
        self.created = time.time() # renew created time for active connecitons

    async def _is_expired(self) -> None:
        return self.expires + int(self.created) < time.time()

    def __repr__(self) -> str:
        return f"Channel uuid={self.channel_uuid} expires={self.expires} encoding={self.encoding}"
    

class ChannelBox:
    """ 
    ChannelBox class.
    
    _CHANNELS: dict, list of active channels
    _CHANNELS_HISTOR: dict, history messages
    _HISTORY_SIZE: int, history size in bytes (you can redefine it with CHANNEL_BOX_HISTORY_SIZE env variable)
    """
    __slots__ = ("_CHANNELS", "_CHANNELS_HISTORY", "_HISTORY_SIZE")
    _CHANNELS: dict = {}
    _CHANNELS_HISTORY: dict = {}
    _HISTORY_SIZE: int = os.getenv("CHANNEL_BOX_HISTORY_SIZE", 1_048_576)
 
    @classmethod
    async def channel_send(cls, channel_name: str="", payload: dict={}, history: bool=False, **kwargs) -> None:
        if history:
            cls._CHANNELS_HISTORY.setdefault(channel_name, [])
            cls._CHANNELS_HISTORY[channel_name].append({"payload": payload, "uuid": shortuuid.uuid(), "datetime": datetime.datetime.now()})
            if sys.getsizeof(cls._CHANNELS_HISTORY[channel_name]) > cls.HISTORY_SIZE:  
                cls._CHANNELS_HISTORY[channel_name] = []

        for channel in cls._CHANNELS.get(channel_name, {}):
            await channel.send(payload)

    @classmethod
    async def channels(cls) -> dict:
        return cls._CHANNELS

    @classmethod
    async def channels_flush(cls) -> None:
        cls._CHANNELS = {}

    @classmethod
    async def history(cls, channel_name: str="") -> list: 
        assert channel_name and isinstance(channel_name, str)
        return cls._CHANNELS_HISTORY.get(channel_name, []) if channel_name else cls._CHANNELS_HISTORY
    
    @classmethod
    async def history_count(cls, channel_name: str) -> int: 
        assert channel_name and isinstance(channel_name, str)
        return len(cls._CHANNELS_HISTORY.get(channel_name, [])) 

    @classmethod     
    async def history_flush(cls) -> None:
        cls._CHANNELS_HISTORY = {}

    @classmethod  
    async def _channel_create(cls, channel_name: str, channel: Channel) -> Enum:

        class ChannelStatus(Enum):
            CREATED = 1
            EXIST = 2 

        status = ChannelStatus.EXIST
        if channel_name not in cls._CHANNELS:
            cls._CHANNELS[channel_name] = {}
            status = ChannelStatus.CREATED      
        cls._CHANNELS[channel_name][channel] = 1
        return status
        
    @classmethod  
    async def _channel_remove(cls, channel_name: str, channel: Channel) -> ChannelBox._clean_expired:
        if channel in cls._CHANNELS.get(channel_name, {}):
            try:
                del cls._CHANNELS[channel_name][channel]
            except:
                logging.debug("no such channel")            
        if not any(cls._CHANNELS.get(channel_name, {})):
            try:
                del cls._CHANNELS[channel_name]
            except:
                logging.debug("no such channel name")
        await cls._clean_expired()

    @classmethod  
    async def _clean_expired(cls) -> None:  
        for channel_name in list(cls._CHANNELS):        
            for channel in cls._CHANNELS.get(channel_name, {}):
                _is_expired = await channel._is_expired()
                if _is_expired:
                    del cls._CHANNELS[channel_name][channel]
            if not any(cls._CHANNELS.get(channel_name, {})):
                try:
                    del cls._CHANNELS[channel_name]
                except Exception as e:
                    logging.debug("no such channel name")


class ChannelBoxEndpoint(WebSocketEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 60 * 60 * 24
        self.encoding = "json"
        self.channel_name = None
        self.channel = None

    async def on_connect(self, websocket: WebSocket, **kwargs) -> None:
        assert isinstance(websocket, WebSocket)
        await super().on_connect(websocket, **kwargs)
        self.channel = Channel(websocket=websocket, expires=self.expires, encoding=self.encoding)

    async def on_disconnect(self, websocket: WebSocket, close_code: int) -> ChannelBox._channel_remove:
        assert isinstance(websocket, WebSocket)
        assert isinstance(close_code, int)
        await super().on_disconnect(websocket, close_code)
        await ChannelBox._channel_remove(self.channel_name, self.channel)

    async def channel_send(self, payload: dict={}, history: bool=False) -> ChannelBox.channel_send:
        assert isinstance(payload, dict)
        assert isinstance(history, bool)
        await ChannelBox.channel_send(self.channel_name, payload, history=history)

    async def get_or_create_named_channel(self, channel_name: str) -> Enum:
        assert channel_name and channel_name.isidentifier(), "Channel names must be valid python identifier only alphanumerics and underscores are accepted"   
        self.channel_name = channel_name
        status = await ChannelBox._channel_create(channel_name, self.channel)
        return status
        


