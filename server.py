from aiohttp import web

from services import send_message

routes = web.RouteTableDef()


@routes.get("/")
async def index_get(request: web.Request) -> web.Response:
    message = request.rel_url.query.get("message")
    if message is not None:
        await send_message(message)
        return web.json_response({"status": "sent"})
    return web.json_response({"status": "error"})


if __name__ == "__main__":
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=5000)
