# channel-box example

Install required dependencies and run server:
``` sh
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8588  
```

Open example:
``` sh
127.0.0.1:8588 
```

Websocket behind the nginx:
``` sh
server {
    server_name your-host.com;

    location / {
        proxy_pass http://127.0.0.1:8588/;

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

Test:
``` sh
tox
```