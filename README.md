# channel-box
`channel-box` it is a simple tool for Starlette & FastAPI framework that allows you send messages to named websocket channels from any part of your code.

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
class Channel(ChannelBoxEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 1600
        self.encoding = "json"

    async def on_connect(self, websocket):
        channel_name = websocket.query_params.get("channel_name", "MySimpleChat")  # channel name */ws?channel_name=MySimpleChat
        await self.channel_get_or_create(channel_name, websocket) 
        await websocket.accept()

    async def on_receive(self, websocket, data):
        message = data["message"]
        username = data["username"]     
        if message.strip():
            payload = {
                "username": username,
                "message": message,
            }
            await self.channel_send(payload, history=True)
```

## Send messages 
Send message to any channel from any part of your code:
```python
from channel_box import channel_box
await channel_box.channel_send(channel_name="MySimpleChat", payload={"username": "Message HTTPEndpoint", "message": "hello from Message"}, history=True) 
```

Get & flush channels:
```python
await channel_box.channels() 
await channel_box.channels_flush()  
```

Get & flush history:
```python
await channel_box.history() 
await channel_box.history_flush()
```






