import os

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings
from starlette.datastructures import Secret

config = Config(".env")
DEBUG = config("DEBUG", cast=bool, default=False)
SITE_HOST = config("SITE_HOST", cast=str, default="127.0.0.1")