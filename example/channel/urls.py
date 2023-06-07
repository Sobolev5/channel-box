from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import WsChatEndpoint
from .views import Chat
from .views import Message
from .views import Groups
from .views import GroupsFlush
from .views import History
from .views import HistoryFlush

routes = [
    WebSocketRoute("/chat_ws", WsChatEndpoint),
    Route("/", endpoint=Chat),
    Route("/message", endpoint=Message),
    Route("/groups", endpoint=Groups),
    Route("/groups-flush", endpoint=GroupsFlush),
    Route("/history", endpoint=History),
    Route("/history-flush", endpoint=HistoryFlush),
]
