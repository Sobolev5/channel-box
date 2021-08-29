from json import JSONDecodeError
from starlette.responses import JSONResponse
from starlette.requests import Request
from simple_print.functions import sprint


async def main(request: Request) -> JSONResponse:
    sprint('channel-box welcome message', c="green")
    return JSONResponse({"channel-box": "welcome"})