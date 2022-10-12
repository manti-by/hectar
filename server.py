import asyncio
import logging
from json import JSONDecodeError

from aiohttp import WSMessage, WSMsgType, web
from aiohttp_apispec import docs, request_schema, setup_aiohttp_apispec
from marshmallow import ValidationError

from schemas import MessageSchema
from services import redis_listener, send_message

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@docs(
    tags=["telegram"],
    summary="Send message API",
    description="This end-point sends message to telegram bot user/users",
)
@request_schema(MessageSchema())
@routes.post("/")
async def index_post(request: web.Request) -> web.Response:
    try:
        payload = await request.json()
    except JSONDecodeError:
        return web.json_response({"status": "Request data is invalid"})

    try:
        schema = MessageSchema()
        data = schema.load(payload)
    except ValidationError as e:
        return web.json_response({"status": "Validation Error", "error": e.messages})

    if data.get("message") is not None:
        await send_message(data.get("message"), data.get("chat_id"))
        return web.json_response({"status": "sent"})
    return web.json_response({"status": "Message error"})


@docs(
    tags=["websockets"],
    summary="Send message to server",
    description="This end-point sends message via websockets",
)
@routes.get("/ws")
async def websockets(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    asyncio.ensure_future(redis_listener(ws))

    async for msg in ws:  # type: WSMessage
        if msg.type == WSMsgType.TEXT:
            if msg.data == "/close":
                await ws.close()
            else:
                await send_message(msg.data)
                await ws.send_str("ok")
        elif msg.type == WSMsgType.ERROR:
            logger.error(
                f"WS connection closed with exception {request.app.ws.exception()}"
            )
    return ws


if __name__ == "__main__":
    app = web.Application()
    setup_aiohttp_apispec(
        app=app,
        title="Hectar Bot documentation",
        version="v1.0",
        url="/api/docs/swagger.json",
        swagger_path="/api/docs",
    )
    app.add_routes(routes)
    web.run_app(app, port=5000)
