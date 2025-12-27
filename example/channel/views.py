import json
from typing import Any
import time
from datetime import datetime
from simple_print import sprint
from jinja2 import Template

from starlette.endpoints import HTTPEndpoint, WebSocketEndpoint
from starlette.responses import HTMLResponse, JSONResponse
from starlette.websockets import WebSocket

from channel_box import Channel, ChannelBox

from .utils import main_template, chat_template


# =========================
# WebSocket example
# =========================

class WsChatEndpoint(WebSocketEndpoint):
    encoding = "text"

    async def on_connect(self, websocket: WebSocket) -> None:
        sprint("WsChatEndpoint.on_connect", c="green")

        await websocket.accept()

        group_name = websocket.query_params.get("group_name")
        if not group_name:
            return

        channel = Channel(
            websocket=websocket,
            expires=60 * 60,
            payload_type="json",
        )

        await ChannelBox.add_channel_to_group(
            channel=channel,
            group_name=group_name,
        )

    async def on_receive(self, websocket: WebSocket, data: Any) -> None:
        sprint(
            f"WsChatEndpoint.on_receive data={data} params={websocket.query_params}",
            c="green",
        )

        try:
            payload = json.loads(data)
        except json.JSONDecodeError:
            return

        message = payload.get("message", "").strip()
        username = payload.get("username", "anonymous")

        if not message:
            return

        group_name = websocket.query_params.get("group_name")
        if not group_name:
            return

        await ChannelBox.group_send(
            group_name=group_name,
            payload={
                "username": username,
                "message": message,
            },
            save_history=True,
        )


# =========================
# HTML demo pages
# =========================

class Chat(HTTPEndpoint):
    async def get(self, request):
        sprint("Chat", c="green")
        return HTMLResponse(Template(main_template).render())


class ChatBase(HTTPEndpoint):
    GROUP_NAME: str

    async def get(self, request):
        sprint("ChatBase.get", c="green")
        return HTMLResponse(
            Template(chat_template).render(
                SOCKET="127.0.0.1:8888",
                GROUP_NAME=self.GROUP_NAME,
            )
        )


class Chat1(ChatBase):
    GROUP_NAME = "MyChat1"


class Chat2(ChatBase):
    GROUP_NAME = "MyChat2"


# =========================
# ChannelBox API examples
# =========================


class SendMessageFromAnyPartOfYourCode(HTTPEndpoint):
    async def get(self, request):
        sprint("SendMessageFromAnyPartOfYourCode", c="green")

        group_name = request.query_params.get("group_name")

        if not group_name:
            return JSONResponse(
                {
                    "status": "error",
                    "detail": "group_name query param is required",
                },
                status_code=400,
            )

        await ChannelBox.group_send(
            group_name=group_name,
            payload={
                "username": "Any part of your code",
                "message": "Hello from backend",
            },
            save_history=True,
        )

        return JSONResponse(
            {
                "status": "ok",
                "group_name": group_name,
            }
        )
    

class ShowGroups(HTTPEndpoint):
    async def get(self, request):
        groups = await ChannelBox.get_groups()

        rows = []

        for group_name, channels in groups.items():
            rows.append(f"""
                <div class="group">
                    <h3>📦 Group: <span>{group_name}</span></h3>
                    <table>
                        <thead>
                            <tr>
                                <th>UUID</th>
                                <th>Payload</th>
                                <th>Expires (s)</th>
                                <th>Last active</th>
                                <th>TTL left</th>
                            </tr>
                        </thead>
                        <tbody>
            """)

            for channel in channels:
                ttl_left = max(0, int(channel.expires - (time.time() - channel.last_active)))
                last_active = datetime.fromtimestamp(channel.last_active).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                rows.append(f"""
                    <tr>
                        <td><code>{channel.uuid}</code></td>
                        <td>{channel.payload_type}</td>
                        <td>{channel.expires}</td>
                        <td>{last_active}</td>
                        <td>{ttl_left}</td>
                    </tr>
                """)

            rows.append("""
                        </tbody>
                    </table>
                </div>
            """)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>ChannelBox — Groups</title>
            <style>
                body {{
                    font-family: system-ui, -apple-system, BlinkMacSystemFont;
                    background: #f5f7fb;
                    padding: 30px;
                }}

                .group {{
                    background: #fff;
                    border-radius: 12px;
                    padding: 20px;
                    margin-bottom: 24px;
                    box-shadow: 0 10px 30px rgba(0,0,0,.08);
                }}

                h3 {{
                    margin-top: 0;
                }}

                h3 span {{
                    color: #4f46e5;
                }}

                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}

                th, td {{
                    padding: 10px;
                    border-bottom: 1px solid #e5e7eb;
                    text-align: left;
                    font-size: 14px;
                }}

                th {{
                    background: #f1f3ff;
                }}

                code {{
                    background: #eef2ff;
                    padding: 4px 6px;
                    border-radius: 6px;
                }}
            </style>
        </head>
        <body>
            <h1>📡 ChannelBox — Active groups</h1>
            {''.join(rows) or '<p>No active groups</p>'}
        </body>
        </html>
        """

        return HTMLResponse(html)
    

class FlushGroups(HTTPEndpoint):
    async def get(self, request):
        sprint("FlushGroups", c="green")
        await ChannelBox.flush_groups()
        return JSONResponse({"flush": "success"})


class ShowHistory(HTTPEndpoint):
    async def get(self, request):
        sprint("ShowHistory", c="green")

        history = await ChannelBox.get_history()

        blocks: list[str] = []

        for group_name, messages in history.items():
            blocks.append(f"""
                <div class="group">
                    <h3>📦 Group: <span>{group_name}</span></h3>
            """)

            if not messages:
                blocks.append("<p class='empty'>No messages</p>")
            else:
                for msg in messages:
                    created = msg.created.strftime("%Y-%m-%d %H:%M:%S")
                    uuid = msg.uuid

                    payload = msg.payload
                    payload_type = type(payload).__name__

                    if isinstance(payload, dict):
                        payload_html = f"<pre>{json.dumps(payload, indent=2, ensure_ascii=False)}</pre>"
                    elif isinstance(payload, bytes):
                        payload_html = f"<code>{payload[:64]!r}...</code>"
                    else:
                        payload_html = f"<div>{payload}</div>"

                    blocks.append(f"""
                        <div class="message">
                            <div class="header">
                                <strong>{payload_type}</strong>
                                <span class="meta">
                                    {created} · {uuid}
                                </span>
                            </div>
                            <div class="body">
                                {payload_html}
                            </div>
                        </div>
                    """)

            blocks.append("</div>")

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>ChannelBox — History</title>
            <style>
                body {{
                    font-family: system-ui, -apple-system, BlinkMacSystemFont;
                    background: #f5f7fb;
                    padding: 30px;
                }}

                h1 {{
                    margin-bottom: 24px;
                }}

                .group {{
                    background: #ffffff;
                    border-radius: 14px;
                    padding: 20px;
                    margin-bottom: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,.08);
                }}

                .group h3 span {{
                    color: #4f46e5;
                }}

                .message {{
                    background: #f8f9ff;
                    border-radius: 12px;
                    padding: 14px;
                    margin-top: 14px;
                }}

                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 8px;
                }}

                .header strong {{
                    color: #4f46e5;
                    font-size: 13px;
                    text-transform: uppercase;
                }}

                .meta {{
                    font-size: 12px;
                    color: #6b7280;
                }}

                .body {{
                    font-size: 14px;
                    white-space: pre-wrap;
                }}

                pre {{
                    background: #eef2ff;
                    padding: 12px;
                    border-radius: 10px;
                    font-size: 13px;
                    margin: 0;
                }}

                code {{
                    background: #eef2ff;
                    padding: 4px 6px;
                    border-radius: 6px;
                }}

                .empty {{
                    color: #9ca3af;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <h1>🕘 ChannelBox — Message history</h1>
            {''.join(blocks) or '<p>No history</p>'}
        </body>
        </html>
        """

        return HTMLResponse(html)
    

class FlushHistory(HTTPEndpoint):
    async def get(self, request):
        sprint("FlushHistory", c="green")
        await ChannelBox.flush_history()
        return JSONResponse({"flush": "success"})


class CleanExpired(HTTPEndpoint):
    async def get(self, request):
        sprint("CleanExpired", c="green")
        await ChannelBox.clean_expired()
        return JSONResponse({"clean_expired": "success"})
