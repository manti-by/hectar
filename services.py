import os

from telegram import Update, Bot
from telegram.ext import ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Start {update.effective_user.first_name}")


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Message {update.effective_user.first_name}")


async def send_message(text: str) -> None:
    bot = Bot(BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=text)
