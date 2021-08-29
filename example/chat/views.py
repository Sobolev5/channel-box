from channel_box import channel_groups
from channel_box import ChannelEndpoint
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from settings import SITE_HOST

html1 = """
<!DOCTYPE html>
<html>
    <head>
        <title>ws</title>
    </head>
    <body>
        <h1>WebsocketChannelEndpoint</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>group_id: </label><input type="text" id="groupId" autocomplete="off" value="group_1"><br/>
            <label>username: </label><input type="text" id="username" autocomplete="off" value="test_user1"><br/>       
            <label>message: </label><input type="text" id="messageText" autocomplete="off" value="test_message1"><br/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://""" + SITE_HOST + """/chat/chat_ws");
            ws.onmessage = function(event) {
                console.log('Message received %s', event.data)
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


class ChatTest1(HTTPEndpoint):
    async def get(self, request):
        channel_groups.groups_show()
        await channel_groups.group_send("group_1", {"username": "ChatTest1 Endpoint", "message": "Notify send from ChatTest1"})
        return HTMLResponse(html1)


html2 = """
<!DOCTYPE html>
<html>
    <head>
        <title>ws</title>
    </head>
    <body>
        <h1>WebsocketChannelEndpoint</h1>
        <form action="" onsubmit="sendMessage(event)">
            <label>group_id: </label><input type="text" id="groupId" autocomplete="off" value="group_2"><br/>
            <label>username: </label><input type="text" id="username" autocomplete="off" value="test_user2"><br/>       
            <label>message: </label><input type="text" id="messageText" autocomplete="off" value="test_message2"><br/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://""" + SITE_HOST + """/chat/chat_ws");
            ws.onmessage = function(event) {
                console.log('Message received %s', event.data)
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


class ChatTest2(HTTPEndpoint):
    async def get(self, request):
        channel_groups.groups_show()
        await channel_groups.group_send("group_2", {"username": "ChatTest2 Endpoint", "message": "Notify send from ChatTest2"})
        return HTMLResponse(html2)


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

            self.get_or_create(group_id)
            payload = {
                "username": username,
                "message": message,
            }
            await self.group_send(payload)
