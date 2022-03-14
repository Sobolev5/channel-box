# ChannelBox
ChannelBox it is a simple tool for Starlette framework that allows you send messages to named websocket channels.

Example of use:
- chats
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

## [important!] See full working example with websocket setup 
```no-highlight
https://channel-box.andrey-sobolev.ru/
https://github.com/Sobolev5/channel-box/tree/master/example
```

## NGINX websocket setup
```no-highlight
http://nginx.org/en/docs/http/websocket.html
```

## Check uvicorn installation
```no-highlight
pip install uvicorn[standard]
```

## channel_box methods

Send message to any group from any part of your code:
```no-highlight
await channel_box.channel_send("MySimpleChat", {"username": "another part code", "message": "hello from SendFromAnotherPartCode"}, show=True, history=True)
```

Show groups and channels:
```no-highlight
await channel_box.channels_show()  
```

Flush all groups and channels:
```no-highlight
await channel_box.channels_flush()
```






