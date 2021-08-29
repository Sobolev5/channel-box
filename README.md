# ChannelBox
ChannelBox it is a simple tool for Starlette framework that allows you send messages to groups of channels.

Example of use:
- chats
- notifications from backend
- alerts 

```no-highlight
https://github.com/Sobolev5/channel-box
```

# Install
To install run:
```no-highlight
pip install channel-box
```

# ChannelEndpoint methods 
Change encoding and expires time on initial (default values is **self.expires = 60 * 60 * 24, self.encoding = "json"**):
```no-highlight
def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.expires = 1600 
    self.encoding = "json"
```


Get or create group by name (only ASCII symbols allowed):
```no-highlight
self.get_or_create('my_chat_1')
self.get_or_create('alert_channel_1')
```


Send message to group:
```no-highlight
await self.group_send('my_chat_1', {"username": "New User", "message": "Hello world"})
await self.group_send('alert_channel_1', {"username": "New User", "message": "Hello world"})
```


# channel_groups methods
Send message to any group from any part of your code:
```no-highlight
await channel_groups.group_send('my_chat_1', {"username": "New User", "message": "Hello world"})
```


Show groups and channels:
```no-highlight
channel_groups.groups_show()
```


Flush all groups and channels:
```no-highlight
channel_groups.groups_flush()
```

# Full working example 
https://github.com/Sobolev5/channel-box/tree/master/example

https://svue-backend.andrey-sobolev.ru/chat/chat1/

https://svue-backend.andrey-sobolev.ru/chat/chat2/


