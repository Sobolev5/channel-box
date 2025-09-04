main_template = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open this chat in different browsers</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    </head>
    <body>
        <div class="container mt-4">        
            <div class="card">
                <div class="card-header">
                    <ul>
                        <li><a href="/chat1" target="_blank">Chat 1</a></li>
                        <li><a href="/chat2" target="_blank">Chat 2</a></li>
                    </ul>
                </div>
            </div>
        </div>
    </body>
</html>
"""

chat_template = """
<!DOCTYPE html>
<html>
    <head>
        <title>Open this chat in different browsers</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
    </head>
    <body>
        <div class="container mt-4">        
            <div class="card">
                <div class="card-header">
                    <h5 class="mt-2">Open this chat in different browsers</h5>
                    <h6>channel-box == 1.1.4</h6>
                    <ul>
                        <li><a href="http://{{ SOCKET }}/send-message-from-any-part-of-your-code" target="_blank">Send message from any part of your code</a></li>
                        <li><a href="http://{{ SOCKET }}/show-groups" target="_blank">Show groups</a></li>
                        <li><a href="http://{{ SOCKET }}/flush-groups" target="_blank">Flush groups</a></li>
                        <li><a href="http://{{ SOCKET }}/show-history" target="_blank">Show history</a></li>
                        <li><a href="http://{{ SOCKET }}/flush-history" target="_blank">Flush history</a></li>
                        <li><a href="http://{{ SOCKET }}/clean-expired" target="_blank">Clean expired</a></li>
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
                var ws = new WebSocket("ws://{{ SOCKET }}/chat_ws?group_name={{ GROUP_NAME }}"); 
                ws.onopen = function(event) {
                    console.log('Connected to websocket. Channel {{ GROUP_NAME }} is open now.')
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
