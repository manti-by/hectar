import os

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from services import start, message

BOT_TOKEN = os.getenv("BOT_TOKEN")


if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(~filters.COMMAND, message))
    app.run_polling()
