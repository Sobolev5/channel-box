# channel-box

`channel-box` is a lightweight async package for **Starlette** and **FastAPI**
that allows you to send messages to **named WebSocket channels (groups)**
from any part of your backend code.

It is designed for simple real-time communication patterns without external
brokers or heavy abstractions.

---

## Features

- Named WebSocket channels (groups)
- Broadcast messages to all connected clients
- Send messages from **any part of the backend**
- Optional message history per group
- Automatic cleanup of disconnected and expired connections
- Fully async, compatible with FastAPI & Starlette
- Zero external infrastructure (no Redis, no RabbitMQ)

---

## Typical use cases

- Group chats  
- Backend notifications  
- Alerts for user groups  
- Real-time status updates  
- Internal dashboards  

---

## Installation

```bash
pip install channel-box
```

---

## Basic usage example

### WebSocket endpoint

```python
import json
from starlette.endpoints import WebSocketEndpoint
from channel_box import Channel, ChannelBox


class WsChatEndpoint(WebSocketEndpoint):

    async def on_connect(self, websocket):
        group_name = websocket.query_params.get("group_name")
        await websocket.accept()

        if not group_name:
            return

        channel = Channel(
            websocket=websocket,
            expires=60 * 60,
            payload_type="json",
        )

        await ChannelBox.add_channel_to_group(
            channel=channel,
            group_name=group_name,
        )

    async def on_receive(self, websocket, data):
        payload = json.loads(data)

        message = payload.get("message")
        username = payload.get("username")

        if not message:
            return

        group_name = websocket.query_params.get("group_name")

        if group_name:
            await ChannelBox.group_send(
                group_name=group_name,
                payload={
                    "username": username,
                    "message": message,
                },
                save_history=True,
            )
```

---

## Send messages from anywhere in backend

```python
from channel_box import ChannelBox

await ChannelBox.group_send(
    group_name="MyChat",
    payload={
        "username": "System",
        "message": "Hello from backend",
    },
    save_history=True,
)
```

---

## Groups management

### Get active groups

```python
groups = await ChannelBox.get_groups()
print(groups)
```

### Flush all groups

```python
await ChannelBox.flush_groups()
```

---

## Message history

### Get history

```python
history = await ChannelBox.get_history()
print(history)
```

### Flush history

```python
await ChannelBox.flush_history()
```

---

## Cleanup expired connections

```python
await ChannelBox.clean_expired()
```

---

## NGINX WebSocket configuration

If you use NGINX as a reverse proxy, make sure WebSocket support is enabled:

```text
http://nginx.org/en/docs/http/websocket.html
```

---

## Uvicorn

```bash
pip install uvicorn[standard]
```

---

## Full working example

```text
https://github.com/Sobolev5/channel-box/tree/master/example
```

---

## Tests

```bash
pytest
```

---

## Repository

```text
https://github.com/Sobolev5/channel-box
```

---

## License

MIT
