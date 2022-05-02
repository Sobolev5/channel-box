import pprint

from channel_box import channel_box
from channel_box import ChannelBoxEndpoint
from starlette.responses import JSONResponse
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse


class ChatChannel(ChannelBoxEndpoint):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.expires = 1600
        self.encoding = "json"

    async def on_connect(self, websocket):
        channel_name = websocket.query_params.get("channel_name", "MySimpleChat")  # channel name */ws?channel_name=MySimpleChat
        await self.channel_get_or_create(channel_name, websocket) # get or create channel
        await websocket.accept()

    async def on_receive(self, websocket, data):

        message = data["message"]
        username = data["username"]

        await channel_box.channels_show()  # show all channels
        
        history = await channel_box.history_get("MySimpleChat") # get channel history
        if history:
            pprint.pprint(history)

        if message.strip():

            payload = {
                "username": username,
                "message": message,
            }

            await self.channel_send(payload, show=True, history=True)
            # show=True - print message process
            # history=True - write history


html = """
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
                var ws = new WebSocket("wss://channel-box.andrey-sobolev.ru/chat_ws?channel_name=MySimpleChat"); 
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


class TestChatChannel(HTTPEndpoint):
    async def get(self, request):           
        return HTMLResponse(html)


class SendFromAnotherPartOfCode(HTTPEndpoint):
    async def get(self, request):       
        # you can catch requests from RabbitMQ for example 
        await channel_box.channel_send("MySimpleChat", {"username": "another part code", "message": "hello from SendFromAnotherPartCode"}, show=True, history=True)  # show all channels    
        history = await channel_box.history_get("MySimpleChat") # get channel history
        if history:
            pprint.pprint(history)
        return JSONResponse({"SendFromAnotherPartOfCode": "success"})


class Flush(HTTPEndpoint):
    async def get(self, request):    
        await channel_box.channels_flush()  
        await channel_box.channels_show()    
        return JSONResponse({"Flush": "success"})
