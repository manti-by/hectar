from json import JSONDecodeError

from aiohttp import web
from aiohttp_apispec import docs, request_schema, setup_aiohttp_apispec
from marshmallow import ValidationError

from schemas import MessageSchema
from services import send_message

routes = web.RouteTableDef()


@docs(
    tags=["telegram"],
    summary="Send message API",
    description="This end-point sends message to telegram",
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

    await send_message(data.get("message"))


if __name__ == "__main__":
    app = web.Application()
    setup_aiohttp_apispec(
        app=app, title="Hectar Bot documentation", version="v1.0",
        url="/api/docs/swagger.json", swagger_path="/api/docs",
    )
    app.add_routes(routes)
    web.run_app(app, port=5000)
