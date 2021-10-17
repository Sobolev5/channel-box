from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import ChatChannel
from .views import TestChatChannel
from .views import SendFromAnotherPartOfCode
from .views import Flush


routes = [
    WebSocketRoute("/chat_ws", ChatChannel),
    Route("/", endpoint=TestChatChannel),
    Route("/send-from-another-part-of-code/", endpoint=SendFromAnotherPartOfCode),
    Route("/flush/", endpoint=Flush),
]
