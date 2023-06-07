# channel-box
`channel-box` it is a package for Starlette & FastAPI framework that allows you send messages to named websocket channels from any part of your code.

Example of use:
- group chats
- notifications from backend
- alerts 


```no-highlight
https://github.com/Sobolev5/channel-box
```

## Install
To install run:
```no-highlight
pip install channel-box
```

## Full working example [1] `example/app.py`
```sh
https://channel-box.andrey-sobolev.ru/
https://github.com/Sobolev5/channel-box/tree/master/example
```

## Full working example [2]
```sh
http://89.108.77.63:1025/
https://github.com/Sobolev5/LordaeronChat  

```
  
___
   

## NGINX websocket setup
```sh
http://nginx.org/en/docs/http/websocket.html
```

## Check uvicorn installation
```sh
pip install uvicorn[standard]
```

## Setup channel 
```python
from starlette.endpoints import WebSocketEndpoint
from channel_box import Channel, ChannelBox

class WsChatEndpoint(WebSocketEndpoint):
    
    async def on_connect(self, websocket):
        group_name = websocket.query_params.get("group_name")  # group name */ws?group_name=MyChat
        if group_name:
            channel = Channel(websocket, expires=60*60, encoding="json") # define user channel
            channel = await ChannelBox.channel_add(group_name, channel) # add channel to named group
        await websocket.accept()

    async def on_receive(self, websocket, data):
        data = json.loads(data)
        message = data["message"]
        username = data["username"]     

        if message.strip():
            payload = {
                "username": username,
                "message": message,
            }
            group_name = websocket.query_params.get("group_name")
            if group_name:
                await ChannelBox.group_send(group_name, payload) # send to all channels
```

## Send messages 
Send message to any channel from any part of your code:
```python
from channel_box import ChannelBox

await ChannelBox.channel_send(channel_name="MyChat", payload={"username": "Message from any part of your code", "message": "hello world"}, history=True) 
```

Get & flush channels:
```python
from channel_box import ChannelBox

await ChannelBox.channels() 
await ChannelBox.channels_flush()  
```

Get & flush history:
```python
from channel_box import ChannelBox

await ChannelBox.history() 
await ChannelBox.history_flush()
```

## Tests
```sh
tox
```