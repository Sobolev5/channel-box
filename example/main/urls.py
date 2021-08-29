from starlette.routing import Route
from .views import main

routes = [
    Route("/", endpoint=main, name="main__main"),
]