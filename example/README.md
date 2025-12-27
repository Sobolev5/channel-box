# ChannelBox Example

This directory contains a **demonstration project** showing how to use **ChannelBox**
to manage named WebSocket channels with **Starlette** and **FastAPI**–style APIs.

This example is **not a library** and **not intended for production use**.
Its purpose is to demonstrate typical ChannelBox usage patterns.

---

## Running the Example

### 1. Install dependencies

Install all required dependencies using the root `pyproject.toml`:

```bash
cd example
poetry install
```

### 2. Run the server

```bash
uvicorn app:app --reload --port 8888
```

### 3. Open in browser

```
http://127.0.0.1:8888
```

---

## WebSocket Groups

The example demonstrates:

- Multiple named WebSocket groups  
- Broadcasting messages to all group members  
- Sending messages from any part of your application code  
- Automatic cleanup of expired connections  
- Optional in-memory message history  

---

## WebSocket Behind Nginx

```nginx
server {
    server_name your-host.com;

    location / {
        proxy_pass http://127.0.0.1:8888;

        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
}
```

---

## ChannelBox with Cron Jobs

Because cron jobs cannot maintain WebSocket connections, the recommended approach
is to expose a small HTTP proxy endpoint and send requests to it.

```python
class ProxySocketInSchema(BaseSchema):
    room_id: str
    type: str
    message: str


@router.post("/proxy_ws", status_code=HTTP_200_OK)
async def proxy_ws(body: ProxySocketInSchema) -> Response:
    await ChannelBox.group_send(
        group_name=body.room_id,
        payload={
            "type": body.type,
            "message": body.message,
        },
    )

    return Response(content="OK", status_code=HTTP_200_OK)
```

---

## Notes

- ChannelBox stores data **in memory**
- This example is **single-process only**
- For multi-process setups, use an external broker (Redis, RabbitMQ, etc.)
