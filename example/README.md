## channel-box chat example

> uvicorn app:app --reload --port 5050  

> yourhostname.com/chat/chat1

> yourhostname.com/chat/chat2

```console
nginx.conf
  map $http_upgrade $connection_upgrade {
    default upgrade; 
    '' close;
  }  

yourhostname.com.conf
 server {
    server_name  yourhostname.com;
    location / {
        proxy_pass http://127.0.0.1:5050/;

        # for websockets
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }  
 }
``` 
