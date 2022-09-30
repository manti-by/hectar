import os

import aiohttp
import aioredis

from telegram import Update, Bot
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

redis = aioredis.from_url("redis://localhost")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.lpush("chats", update.effective_chat.id)

    chat_ids = []
    chat_len = await redis.llen("chats")
    for index in range(chat_len):
        chat_id = await redis.lindex("chats", index)
        chat_ids.append(chat_id.decode())

    await update.message.reply_text(", ".join(set(chat_ids)))


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Message {update.effective_user.first_name}")


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


async def send_message(text: str) -> None:
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)
