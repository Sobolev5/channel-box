# channel-box
`channel-box` it is a package for Starlette & FastAPI frameworks that allows 
you send messages to named websocket channels from any part of your code.

Example of use:
- group chats
- notifications from backend
- alerts for user groups


```no-highlight
https://github.com/Sobolev5/channel-box
```

## Install
To install run:
```no-highlight
pip install channel-box
```

## Full working example
```sh
https://github.com/Sobolev5/channel-box/tree/master/example
```


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
        group_name = websocket.query_params.get(
            "group_name"
        )  # group name */ws?group_name=MyChat
        if group_name:
            channel = Channel(
                websocket,
                expires=60 * 60,
                payload_type="json",
            )  # Create new user channel
            await ChannelBox.add_channel_to_group(
                channel=channel,
                group_name=group_name,
            )  # Add channel to named group
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
                await ChannelBox.group_send(
                    group_name=group_name,
                    payload=payload,
                    save_history=True,
                ) # Send to all user channels
```

## Send messages 
Send message to any channel from any part of your code:

```python
from channel_box import ChannelBox

await ChannelBox.group_send(
    group_name="MyChat", 
    payload={
        "username": "Message from any part of your code", 
        "message": "hello world"
    }, 
    save_history=True,
) 
```

Get & flush groups:
```python
from channel_box import ChannelBox

groups = await ChannelBox.get_groups() 
print(groups)
await ChannelBox.flush_groups()  
```

Get & flush history:
```python
from channel_box import ChannelBox

history = await ChannelBox.get_history() 
print(history)
await ChannelBox.flush_history()
```

Clean expired:
```python
from channel_box import ChannelBox

await ChannelBox.clean_expired() 
```

## Tests
```sh
tox
```