from __future__ import annotations
import datetime
import sys
import os
import time
import uuid
import logging
from enum import Enum
from starlette.websockets import WebSocket
from starlette.endpoints import WebSocketEndpoint


class Channel:
    """ 
    Channel class.

    websocket: WebSocket # Starlette websocket instance (see starlette documentation)
    expires: int -> Channel ttl in seconds
    encoding: str [json, text, bytes] -> Encoding of sending data
    uuid: str -> Unique identifier of channnel
    created: time, channel creation time
    """ 
    def __init__(self, websocket: WebSocket, expires: int, encoding: str) -> None:       
        assert isinstance(websocket, WebSocket)
        assert isinstance(expires, int)
        assert isinstance(encoding, str) and encoding in ["json", "text", "bytes"], "Must be in ['json', 'text', 'bytes']"
        self.websocket = websocket
        self.expires = expires
        self.encoding = encoding
        self.uuid = uuid.uuid4()
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
        return f"Channel uuid={self.uuid} expires={self.expires} encoding={self.encoding}"
    

class ChannelBox:
    """ 
    ChannelBox class.
    
    _GROUPS: dict, dict with groups of active channels ~ key: group_name, val: list of channels
    _GROUPS_HISTORY: dict, history messages
    _HISTORY_SIZE: int, history size in bytes (you can redefine it with CHANNEL_BOX_HISTORY_SIZE env variable)
    """

    _GROUPS: dict = {}
    _GROUPS_HISTORY: dict = {}
    _HISTORY_SIZE: int = os.getenv("CHANNEL_BOX_HISTORY_SIZE", 1_048_576)
 
    @classmethod
    async def group_send(cls, group_name: str="", payload: dict={}, history: bool=False, **kwargs) -> None:
        if history:
            cls._GROUPS_HISTORY.setdefault(group_name, [])
            cls._GROUPS_HISTORY[group_name].append({"payload": payload, "uuid": uuid.uuid4(), "datetime": datetime.datetime.now()})
            if sys.getsizeof(cls._GROUPS_HISTORY[group_name]) > cls._HISTORY_SIZE:  
                cls._GROUPS_HISTORY[group_name] = []

        for channel in cls._GROUPS.get(group_name, {}):
            await channel.send(payload)

    @classmethod
    async def channels(cls) -> dict:
        return cls._GROUPS

    @classmethod
    async def channels_flush(cls) -> None:
        cls._GROUPS = {}

    @classmethod
    async def history(cls, group_name: str="") -> dict: 
        return cls._GROUPS_HISTORY.get(group_name, {}) if group_name else cls._GROUPS_HISTORY
    
    @classmethod
    async def history_count(cls, group_name: str) -> int: 
        assert group_name and isinstance(group_name, str)
        return len(cls._GROUPS_HISTORY.get(group_name, [])) 

    @classmethod     
    async def history_flush(cls) -> None:
        cls._GROUPS_HISTORY = {}

    @classmethod  
    async def channel_add(cls, group_name: str, channel: Channel) -> Enum:

        class GroupStatus(Enum):
            ADDED = 1
            EXIST = 2 

        status = GroupStatus.EXIST
        if group_name not in cls._GROUPS:
            cls._GROUPS[group_name] = {}
            status = GroupStatus.ADDED      
        cls._GROUPS[group_name][channel] = 1
        return status
        
    @classmethod  
    async def channel_remove(cls, group_name: str, channel: Channel) -> ChannelBox._clean_expired:
        if channel in cls._GROUPS.get(group_name, {}):
            try:
                del cls._GROUPS[group_name][channel]
            except:
                logging.debug("no such channel")            
        if not any(cls._GROUPS.get(group_name, {})):
            try:
                del cls._GROUPS[group_name]
            except:
                logging.debug("no such group")
        await cls._clean_expired()

    @classmethod  
    async def _clean_expired(cls) -> None:  
        for group_name in list(cls._GROUPS):        
            for channel in cls._GROUPS.get(group_name, {}):
                _is_expired = await channel._is_expired()
                if _is_expired:
                    del cls._GROUPS[group_name][channel]
            if not any(cls._GROUPS.get(group_name, {})):
                try:
                    del cls._GROUPS[group_name]
                except Exception as e:
                    logging.debug("no such group")



