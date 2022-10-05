import os

import aiohttp
import aioredis

from telegram import Update, Bot
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

redis = aioredis.from_url(f"redis://{REDIS_HOST}")


async def get_chat_ids():
    chat_ids = []
    chat_len = await redis.llen("chats")
    for index in range(chat_len):
        chat_id = await redis.lindex("chats", index)
        chat_ids.append(chat_id.decode())
    return list(set(chat_ids))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.lpush("chats", update.effective_chat.id)

    chat_ids = await get_chat_ids()
    await update.message.reply_text(", ".join(set(chat_ids)))


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.publish("messages", update.message.text)


async def top_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await get_products("http://127.0.0.1:8000/api/products/?ordering=-cost", update, context)


async def popular_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await get_products("http://127.0.0.1:8000/api/products/popular/", update, context)


async def get_products(url: str, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            products = await response.json()
    result = ""
    for product in products["results"]:
        result += f"{product['title']} - {product['cost']}\n"
    await update.message.reply_text(result)


async def send_message(text: str, chat_id: int = None) -> None:
    bot = Bot(BOT_TOKEN)
    if chat_id is not None:
        await bot.send_message(chat_id=chat_id, text=text)
        return
    for chat_id in await get_chat_ids():
        await bot.send_message(chat_id=chat_id, text=text)


async def redis_subscriber(ws):
    async with redis.pubsub() as channel:
        await channel.subscribe("messages")
        async for response in channel.listen():
            if isinstance(response.get("data"), bytes):
                await ws.send_str(response.get('data').decode())
            else:
                await ws.send_str(f"Pubsub channel: {response.get('data')}")
