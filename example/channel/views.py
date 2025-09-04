import json

from simple_print import sprint
from jinja2 import Template

from channel_box import Channel
from channel_box import ChannelBox

from .utils import main_template
from .utils import chat_template

from starlette.endpoints import WebSocketEndpoint
from starlette.responses import JSONResponse
from starlette.endpoints import HTTPEndpoint
from starlette.responses import HTMLResponse


class WsChatEndpoint(WebSocketEndpoint):
    async def on_connect(
        self,
        websocket,
    ):
        sprint(
            f"{self.__class__.__name__}.on_connect",
            c="green",
        )

        group_name = websocket.query_params.get(
            "group_name",
        )

        if group_name:
            channel = Channel(
                websocket,
                expires=60 * 60,
                payload_type="json",
            )

            await ChannelBox.add_channel_to_group(
                channel=channel,
                group_name=group_name,
            )

        await websocket.accept()

    async def on_receive(
        self,
        websocket,
        data,
    ):
        sprint(
            f"{self.__class__.__name__}.on_receive {data=} {websocket.query_params=}",
            c="green",
        )

        data = json.loads(
            data,
        )

        message = data["message"]

        username = data["username"]

        if message.strip():
            payload = {
                "username": username,
                "message": message,
            }

            group_name = websocket.query_params.get(
                "group_name",
            )

            if group_name:
                await ChannelBox.group_send(
                    group_name=group_name,
                    payload=payload,
                    save_history=True,
                )


class Chat(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        template = Template(
            main_template,
        )

        return HTMLResponse(
            template.render(),
        )


class Chat1(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        template = Template(
            chat_template,
        )

        return HTMLResponse(
            template.render(
                SOCKET="127.0.0.1:8888",
                GROUP_NAME="MyChat1",
            ),
        )


class Chat2(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        template = Template(
            chat_template,
        )

        return HTMLResponse(
            template.render(
                SOCKET="127.0.0.1:8888",
                GROUP_NAME="MyChat2",
            ),
        )


class SendMessageFromAnyPartOfYourCode(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        await ChannelBox.group_send(
            group_name="MyChat",
            payload={
                "username": "Any part of your code",
                "message": "Hello World",
            },
            save_history=True,
        )

        return JSONResponse(
            {
                "message": "success",
            },
        )


class ShowGroups(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        groups = await ChannelBox.get_groups()

        return JSONResponse(
            groups,
        )


class FlushGroups(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        await ChannelBox.flush_groups()

        return JSONResponse(
            {
                "flush": "success",
            },
        )


class ShowHistory(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        history = await ChannelBox.get_history()

        return JSONResponse(
            history,
        )


class FlushHistory(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        await ChannelBox.flush_history()

        return JSONResponse(
            {
                "flush": "success",
            },
        )


class CleanExpired(HTTPEndpoint):
    async def get(
        self,
        request,
    ):
        sprint(
            f"{self.__class__.__name__}",
            c="green",
        )

        await ChannelBox.clean_expired()

        return JSONResponse(
            {
                "clean_expired": "success",
            },
        )
