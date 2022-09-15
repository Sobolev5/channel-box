import sys
from pathlib import Path
sys.path.append(str(Path('.').absolute().parent)) 

from starlette.applications import Starlette
from starlette.routing import Mount
from channel.urls import routes as channel_routes


routes = [
    Mount("/", routes=channel_routes),
]


app = Starlette(debug=True, routes=routes)
