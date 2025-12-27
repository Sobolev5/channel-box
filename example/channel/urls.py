from starlette.routing import Route, WebSocketRoute

from .views import (
    WsChatEndpoint,
    Chat,
    Chat1,
    Chat2,
    SendMessageFromAnyPartOfYourCode,
    ShowGroups,
    FlushGroups,
    ShowHistory,
    FlushHistory,
    CleanExpired,
)


routes = [
    # WebSocket example
    WebSocketRoute("/chat_ws", WsChatEndpoint),

    # HTTP demo pages
    Route("/", Chat),
    Route("/chat1", Chat1),
    Route("/chat2", Chat2),

    # ChannelBox interaction examples
    Route("/send-message-from-any-part-of-your-code", SendMessageFromAnyPartOfYourCode),
    Route("/show-groups", ShowGroups),
    Route("/flush-groups", FlushGroups),

    # History management examples
    Route("/show-history", ShowHistory),
    Route("/flush-history", FlushHistory),

    # Maintenance
    Route("/clean-expired", CleanExpired),
]
