from simple_print import sprint
from jinja2 import Template
from channel_box import channel_box
from channel_box import ChannelBoxEndpoint
from starlette.responses import JSONResponse
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from settings import HOST

class Channel(ChannelBoxEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 16000
        self.encoding = "json"

    async def on_connect(self, websocket):
        sprint('user_connected', c="green", p=True)
        channel_name = websocket.query_params.get("channel_name", "MySimpleChat")  # channel name */ws?channel_name=MySimpleChat
        await self.channel_get_or_create(channel_name, websocket) 
        await websocket.accept()

    async def on_receive(self, websocket, data):
        message = data["message"]
        username = data["username"]     
        if message.strip():
            payload = {
                "username": username,
                "message": message,
            }
            await self.channel_send(payload, history=True)


html_text = """
<!DOCTYPE html>
<html>
    <head>
        <title>MySimpleChat channel (open in different browsers)</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    </head>
    <body>
        <div class="container mt-4">
            
            <div class="card">
                <div class="card-header">
                    <h5 class="mt-2">MySimpleChat channel (open in different browsers)</h5>
                    <h5>channel-box == 0.4.0</h5>
                    <ul>
                        <li><a href="http://{{ host }}/message" target="_blank">Send message from another view</a></li>
                        <li><a href="http://{{ host }}/channels" target="_blank">Show channels</a></li>
                        <li><a href="http://{{ host }}/channels-flush" target="_blank">Flush channels</a></li>
                        <li><a href="http://{{ host }}/history" target="_blank">Show history</a></li>
                        <li><a href="http://{{ host }}/history-flush" target="_blank">Flush history</a></li>
                    </ul>
                </div>
                <div class"card-body">   
                    <div class="p-3">                 
                        <form onsubmit="sendMessage(event)">
                            <div class="mb-3">
                                <label for="username" class="form-label">Username</label>
                                <input type="username" class="form-control" id="username" aria-describedby="username" value="root">
                            </div>
                            <div class="mb-3">
                                <label for="message" class="form-label">Message</label>
                                <input type="message" class="form-control" id="message" aria-describedby="username" value="Lorem ipsum">
                            </div>
                            <button type="submit" class="btn btn-primary">Submit</button>
                        </form>
                    </div>
                    <div class="p-3"> 
                        <div id="messages">
                        </div>
                    </div>
                </div>
            </div>
            <script>
                var ws = new WebSocket("wss://{{ host }}/chat_ws?channel_name=MySimpleChat"); 
                ws.onopen = function(event) {
                    console.log('Connected to websocket. Channel MySimpleChat is open now.')
                };
                ws.onmessage = function(event) {
                    console.log('Message received %s', event.data)
                    var messages = document.getElementById('messages');
                    var message = document.createElement('div');
                    var data = JSON.parse(event.data);
                    message.innerHTML = `<strong>${data.username} :</strong> ${data.message}`;
                    messages.appendChild(message);
                };
                function sendMessage(event) {
                    var username = document.getElementById("username");
                    var message = document.getElementById("message");
                    var data = {
                        "username": username.value,
                        "message": message.value,
                    };
                    console.log('Message send %s', data)
                    ws.send(JSON.stringify(data));
                    event.preventDefault();
                }
            </script>
        </div>
    </body>
</html>
"""

class Chat(HTTPEndpoint):
    async def get(self, request):   
        template = Template(html_text)      
        return HTMLResponse(template.render(host=HOST))

class Message(HTTPEndpoint):
    async def get(self, request):     
        await channel_box.channel_send(channel_name="MySimpleChat", payload={"username": "Message HTTPEndpoint", "message": "hello from Message"}, history=True)   
        return JSONResponse({"message": "success"})

class Channels(HTTPEndpoint):
    async def get(self, request):                 
        channels = await channel_box.channels()
        return HTMLResponse(f"{channels}")

class ChannelsFlush(HTTPEndpoint):
    async def get(self, request):   
        await channel_box.channels_flush()            
        return JSONResponse({"flush": "success"})   

class History(HTTPEndpoint):
    async def get(self, request):      
        history = await channel_box.history()
        return HTMLResponse(f"{history}")

class HistoryFlush(HTTPEndpoint):
    async def get(self, request):  
        await channel_box.history_flush()             
        return JSONResponse({"flush": "success"})




