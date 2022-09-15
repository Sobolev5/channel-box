from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import Channel
from .views import Chat
from .views import Message
from .views import Channels
from .views import ChannelsFlush
from .views import History
from .views import HistoryFlush

routes = [
    WebSocketRoute("/chat_ws", Channel),
    Route("/", endpoint=Chat),
    Route("/message", endpoint=Message),
    Route("/channels", endpoint=Channels),
    Route("/channels-flush", endpoint=ChannelsFlush),
    Route("/history", endpoint=History),
    Route("/history-flush", endpoint=HistoryFlush),
]
