import os

import aiohttp
from telegram import Update, Bot
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Start {update.effective_user.first_name}")


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Message {update.effective_user.first_name}")


async def top_products(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with aiohttp.ClientSession() as session:
        async with session.get("http://127.0.0.1:8000/api/products/?ordering=-cost") as response:
            products = await response.json()
    result = ""
    for product in products["results"]:
        result += f"{product['title']} - {product['cost']}\n"
    await update.message.reply_text(result)


async def send_message(text: str) -> None:
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)
