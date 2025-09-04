from starlette.routing import Route
from starlette.routing import WebSocketRoute

from .views import WsChatEndpoint
from .views import Chat
from .views import Chat1
from .views import Chat2
from .views import SendMessageFromAnyPartOfYourCode
from .views import ShowGroups
from .views import FlushGroups
from .views import ShowHistory
from .views import FlushHistory
from .views import CleanExpired


routes = [
    WebSocketRoute("/chat_ws", WsChatEndpoint),
    Route("/", endpoint=Chat),
    Route("/chat1", endpoint=Chat1),
    Route("/chat2", endpoint=Chat2),
    Route(
        "/send-message-from-any-part-of-your-code",
        endpoint=SendMessageFromAnyPartOfYourCode,
    ),
    Route("/show-groups", endpoint=ShowGroups),
    Route("/flush-groups", endpoint=FlushGroups),
    Route("/show-history", endpoint=ShowHistory),
    Route("/flush-history", endpoint=FlushHistory),
    Route("/clean-expired", endpoint=CleanExpired),
]
