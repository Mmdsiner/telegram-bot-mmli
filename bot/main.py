import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TOKEN
from handlers.user import start, user_handler
from handlers.admin import admin_handler
from database import init_db

async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(user_handler)
    app.add_handler(admin_handler)

    await init_db()
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
