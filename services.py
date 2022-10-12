import logging
import os

import aiohttp
import aioredis
from telegram import Bot, Update
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

logger = logging.getLogger(__name__)
redis = aioredis.from_url("redis://localhost")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.lpush("chats", update.effective_chat.id)
    await update.message.reply_text("ok")


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.publish("messages", update.message.text)
    await update.message.reply_text("ok")


async def redis_listener(ws):
    async with redis.pubsub() as channel:
        await channel.subscribe("messages")
        async for response in channel.listen():
            if isinstance(response.get("data"), bytes):
                await ws.send_str(response.get("data").decode())
            else:
                logger.info(f"pubsub channel: {response.get('data')}")


async def chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_ids = []
    chats_len = await redis.llen("chats")
    for index in range(0, chats_len):
        chat_id = await redis.lindex("chats", index)
        chat_ids.append(chat_id.decode())
    await update.message.reply_text(f"Chats: {', '.join(chat_ids)}")


async def top_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(
            "http://127.0.0.1:8000/api/products/?ordering=-cost"
        ) as response:
            if response.status == 200:
                products = await response.json()
                result = ""
                for product in products["results"]:
                    result += f"{product['title']} - {product['cost']}\n"
            else:
                result = f"Blog API returned HTTP code {response.status}"
            await update.message.reply_text(result)


async def get_chart_ids():
    return list(
        set(
            [
                int(await redis.lindex("chats", index))
                for index in range(await redis.llen("chats"))
            ]
        )
    )


async def send_message(text: str, chat_id: int = None) -> None:
    bot = Bot(BOT_TOKEN)
    if chat_id is not None:
        await bot.send_message(chat_id=chat_id, text=text)
        return
    for chat_id in await get_chart_ids():
        await bot.send_message(chat_id=chat_id, text=text)


async def subscribe_to_redis_channel():
    async with redis.pubsub() as channel:
        await channel.subscribe("messages")
        async for response in channel.listen():
            logger.info(response.get("data"))


async def send_ws_message():
    async with aiohttp.ClientSession() as session:
        async with session.ws_connect("http://127.0.0.1:5000/ws") as ws:
            await ws.send_str("Message from console")
