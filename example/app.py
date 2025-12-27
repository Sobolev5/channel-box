from starlette.applications import Starlette
from starlette.routing import Mount

from example.channel.urls import routes as channel_routes


def create_app() -> Starlette:
    return Starlette(
        debug=True,
        routes=[
            Mount("/", routes=channel_routes),
        ],
    )


app = create_app()
