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
    await update.message.reply_text(f"Start {update.effective_user.first_name}")


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await redis.lpush("messages", {"chat_id": update.effective_chat.id, "text": update.message.text})
    await update.message.reply_text(f"Message {update.effective_user.first_name}")


async def chats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_ids = []
    chats_len = await redis.llen("chats")
    for index in range(0, chats_len):
        chat_id = await redis.lindex("chats", index)
        chat_ids.append(chat_id.decode())
    await update.message.reply_text(f"Chats: {', '.join(chat_ids)}")


async def top_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8000/api/products/?ordering=-cost") as response:
            if response.status == 200:
                products = await response.json()
                result = ""
                for product in products["results"]:
                    result += f"{product['title']} - {product['cost']}\n"
            else:
                result = f"Blog API returned HTTP code {response.status}"
            await update.message.reply_text(result)


async def send_message(text: str, chat_id: int = None) -> None:
    bot = Bot(BOT_TOKEN)
    if chat_id is None:
        for index in range(1, redis.llen("chats") + 1):
            chat_id = await redis.lindex("chats", index)
            await bot.send_message(chat_id=chat_id, text=text)
    await bot.send_message(chat_id=chat_id, text=text)
