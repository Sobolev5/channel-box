# ChannelBox
ChannelBox is a convenient tool for Starlette framework that allows you send messages to groups of channels.

Example of use:
- chats
- notifications from backend
- alerts 

```no-highlight
https://github.com/Sobolev5/channel-box
```

# How to use it
To install run:
```no-highlight
pip install channel-box
```


Modify your urls.py:
```python
from starlette.routing import Route
from starlette.routing import WebSocketRoute
from .views import ChatView
from .views import ChatSocket

routes = [
    Route("/", endpoint=ChatView),
    WebSocketRoute("/chat_ws", ChatSocket),
]
```


Add the following lines to your views.py file:
```python
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from channel_box import ChannelEndpoint
from channel_box import group_send
from channel_box import groups_show
from channel_box import groups_flush

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>ws</title>
    </head>
    <body>
        <h1>WebsocketChannelEndpoint</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>group_id: </label><input type="text" id="groupId" autocomplete="off" value="1"><br/>
            <label>username: </label><input type="text" id="username" autocomplete="off" value="test_user1"><br/>       
            <label>message: </label><input type="text" id="messageText" autocomplete="off" value="test_message1"><br/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost/chat_ws");
            ws.onmessage = function(event) {
                console.log('Message recivied %s', event.data)
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var data = JSON.parse(event.data);
                message.innerHTML = `<strong>${data.username} :</strong> ${data.message}`;
                messages.appendChild(message);
            };
            function sendMessage(event) {
                var username = document.getElementById("username");
                var group_id = document.getElementById("groupId");
                var input = document.getElementById("messageText");
                var data = {
                    "group_id": group_id.value, 
                    "username": username.value,
                    "message": input.value,
                };
                console.log('Message send %s', data)
                ws.send(JSON.stringify(data));
                event.preventDefault();
            }
        </script>
    </body>
</html>
"""

class ChatView(HTTPEndpoint):

    async def get(self, request):
        groups_show()
        await group_send("group_1", {"username": "send from ChatView", "message": "Hello from ChatView"})
        return HTMLResponse(html1)

class ChatSocket(ChannelEndpoint):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 1600 
        self.encoding = "json"

    async def on_receive(self, websocket, data):
        group_id = data["group_id"]
        message = data["message"]
        username = data["username"]
        if message.strip():
            group = f"group_{group_id}"
            await self.get_or_create(group)
            payload = {
                "username": username,
                "message": message,
            }
            await self.group_send(payload)
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
await self.get_or_create('my_chat_1')
await self.get_or_create('alert_channel_1')
```


Send message to group:
```no-highlight
self.group_send('my_chat_1', {"username": "New User", "message": "Hello world"})
self.group_send('alert_channel_1', {"a": "New User", "message": "Hello world"})
```


# Global functions
Send message to group from any part of your code:
```no-highlight
await group_send('my_chat_1', {"username": "New User", "message": "Hello world"})
```


Show groups and channels:
```no-highlight
groups_show()
```


Flush all groups and channels:
```no-highlight
groups_flush()
```

# Working example 
https://github.com/Sobolev5/starlette-vue-backend/tree/master/apps/chat

http://backend.starlette-vue.site/chat/chat1/

http://backend.starlette-vue.site/chat/chat2/


