import json
from simple_print import sprint
from jinja2 import Template
from channel_box import Channel
from channel_box import ChannelBox
from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse
from settings import SOCKET


class WsChatEndpoint(WebSocketEndpoint):

    async def on_connect(self, websocket):
        sprint('Channel.on_connect', c="green")
        group_name = websocket.query_params.get("group_name")  # group name */ws?group_name=MyChat
        if group_name:
            channel = Channel(websocket, expires=60*60, encoding="json") # define user channel
            status = await ChannelBox.channel_add(group_name, channel) # add channel to named group
        await websocket.accept()

    async def on_receive(self, websocket, data):
        sprint(f'Channel.on_receive data [{data}]', c="green")
        data = json.loads(data)
        message = data["message"]
        username = data["username"]     

        if message.strip():
            payload = {
                "username": username,
                "message": message,
            }
            group_name = websocket.query_params.get("group_name")
            if group_name:
                await ChannelBox.group_send(group_name, payload, history=True)

html_text = """
<!DOCTYPE html>
<html>
    <head>
        <title>MyChat group (open in different browsers)</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    </head>
    <body>
        <div class="container mt-4">        
            <div class="card">
                <div class="card-header">
                    <h5 class="mt-2">MyChat group (open in different browsers)</h5>
                    <h5>channel-box == 0.5.0</h5>
                    <ul>
                        <li><a href="http://{{ SOCKET }}/message" target="_blank">Send message from another view</a></li>
                        <li><a href="http://{{ SOCKET }}/groups" target="_blank">Show groups</a></li>
                        <li><a href="http://{{ SOCKET }}/groups-flush" target="_blank">Flush groups</a></li>
                        <li><a href="http://{{ SOCKET }}/history" target="_blank">Show history</a></li>
                        <li><a href="http://{{ SOCKET }}/history-flush" target="_blank">Flush history</a></li>
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
                var ws = new WebSocket("ws://{{ SOCKET }}/chat_ws?group_name=MyChat"); 
                ws.onopen = function(event) {
                    console.log('Connected to websocket. Channel MyChat is open now.')
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
        sprint('Chat.get', c="green")    
        template = Template(html_text)      
        return HTMLResponse(template.render(SOCKET=SOCKET))

class Message(HTTPEndpoint):
    async def get(self, request):   
        sprint('Message.get', c="green")          
        await ChannelBox.group_send(group_name="MyChat", payload={"username": "Any part of your code", "message": "Hello World"}, history=True)   
        return JSONResponse({"message": "success"})

class Groups(HTTPEndpoint):
    async def get(self, request):  
        sprint('Groups.get', c="green")                 
        groups = await ChannelBox.groups()
        return HTMLResponse(f"{groups}")

class GroupsFlush(HTTPEndpoint):
    async def get(self, request): 
        sprint('GroupsFlush.get', c="green")    
        await ChannelBox.groups_flush()            
        return JSONResponse({"flush": "success"})   

class History(HTTPEndpoint):
    async def get(self, request):   
        sprint('History.get', c="green")   
        history = await ChannelBox.history()
        return HTMLResponse(f"{history}")

class HistoryFlush(HTTPEndpoint):
    async def get(self, request):  
        sprint('HistoryFlush.get', c="green")
        await ChannelBox.history_flush()             
        return JSONResponse({"flush": "success"})




