# ChannelBox example

Install required dependencies from pyproject.toml 
at the root directory and run server:
```
poetry install
uvicorn app:app --reload --host 0.0.0.0 --port 8888  
```

Open example:
```
127.0.0.1:8888 
```

Websocket behind the Nginx:
``` 
server {
    server_name your-host.com;

    location / {
        proxy_pass http://127.0.0.1:8888/;

        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # for websockets
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
}

```

# ChannelBox via cron jobs.
If you want to make alerts from cron jobs, you need to
make api proxy on you live app and send http requests on this
proxy from cron jobs. 

```
class ProxySocketInSchema(BaseSchema):
    room_id: str
    type: str
    message: str


@router.post(
    "/proxy_ws",
    status_code=HTTP_200_OK,
)
async def proxy_ws(
    body: ProxySocketInSchema,
) -> Response:
    await ChannelBox.group_send(
        group_name=body.room_id,
        payload={
            "type": body.type,
            "message": body.message,
        },
    )

    return Response(
        content="OK",
        status_code=HTTP_200_OK,
    )

```
  