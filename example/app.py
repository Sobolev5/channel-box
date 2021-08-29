from starlette.applications import Starlette
from starlette.routing import Mount
from chat.urls import routes as chat_routes
from main.urls import routes as main_routes
from settings import DEBUG


routes = [
    Mount("/chat", routes=chat_routes),
    Mount("/", routes=main_routes),
]


app = Starlette(debug=DEBUG, routes=routes)


