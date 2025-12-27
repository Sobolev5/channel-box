main_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ChannelBox demo</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
          rel="stylesheet">

    <style>
        body {
            background: #f5f7fb;
        }
        .card {
            border-radius: 12px;
        }
        .chat-link a {
            text-decoration: none;
            font-weight: 500;
        }
    </style>
</head>
<body>

<div class="container mt-5">
    <div class="card shadow-sm">
        <div class="card-header bg-dark text-white">
            <h5 class="mb-0">ChannelBox demo</h5>
        </div>

        <div class="card-body">
            <p class="text-muted">
                Open the same chat in different browsers or tabs:
            </p>

            <ul class="list-group list-group-flush chat-link">
                <li class="list-group-item">
                    <a href="/chat1" target="_blank">💬 Chat 1</a>
                </li>
                <li class="list-group-item">
                    <a href="/chat2" target="_blank">💬 Chat 2</a>
                </li>
            </ul>
        </div>
    </div>
</div>

</body>
</html>
"""


chat_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ChannelBox chat</title>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css"
          rel="stylesheet">

    <style>
        body {
            background: #f5f7fb;
        }

        .card {
            border-radius: 12px;
        }

        .chat-box {
            max-height: 350px;
            overflow-y: auto;
            background: #ffffff;
            border-radius: 8px;
            padding: 15px;
            border: 1px solid #e5e7eb;
        }

        .chat-message {
            margin-bottom: 8px;
            padding: 6px 10px;
            background: #eef2ff;
            border-radius: 6px;
        }

        .chat-message strong {
            color: #3b5bdb;
        }

        .form-control {
            border-radius: 8px;
        }
    </style>
</head>
<body>

<div class="container mt-5">
    <div class="card shadow-sm">
        <div class="card-header bg-dark text-white">
            <h5 class="mb-1">ChannelBox chat</h5>
            <small class="text-muted">channel-box == 1.2.0</small>
        </div>

        <div class="card-body">

            <ul class="small mb-4">
                <li><a href="http://{{ SOCKET }}/send-message-from-any-part-of-your-code?group_name={{ GROUP_NAME }}" target="_blank">Send message from code</a></li>
                <li><a href="http://{{ SOCKET }}/show-groups" target="_blank">Show groups</a></li>
                <li><a href="http://{{ SOCKET }}/flush-groups" target="_blank">Flush groups</a></li>
                <li><a href="http://{{ SOCKET }}/show-history" target="_blank">Show history</a></li>
                <li><a href="http://{{ SOCKET }}/flush-history" target="_blank">Flush history</a></li>
                <li><a href="http://{{ SOCKET }}/clean-expired" target="_blank">Clean expired</a></li>
            </ul>

            <form onsubmit="sendMessage(event)" class="mb-4">
                <div class="row g-2">
                    <div class="col-md-3">
                        <input class="form-control" id="username" value="root" placeholder="Username">
                    </div>
                    <div class="col-md-7">
                        <input class="form-control" id="message" value="Lorem ipsum" placeholder="Message">
                    </div>
                    <div class="col-md-2 d-grid">
                        <button class="btn btn-primary">Send</button>
                    </div>
                </div>
            </form>

            <div id="messages" class="chat-box"></div>

        </div>
    </div>
</div>

<script>
    var ws = new WebSocket("ws://{{ SOCKET }}/chat_ws?group_name={{ GROUP_NAME }}");

    ws.onopen = function () {
        console.log("Connected to channel {{ GROUP_NAME }}");
    };

    ws.onmessage = function (event) {
        var data = JSON.parse(event.data);
        var messages = document.getElementById("messages");

        var div = document.createElement("div");
        div.className = "chat-message";
        div.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;

        messages.appendChild(div);
        messages.scrollTop = messages.scrollHeight;
    };

    function sendMessage(event) {
        event.preventDefault();

        var data = {
            username: document.getElementById("username").value,
            message: document.getElementById("message").value,
        };

        ws.send(JSON.stringify(data));
    }
</script>

</body>
</html>
"""
