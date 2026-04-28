from telegram.ext import ApplicationBuilder
from config import TOKEN
from handlers.user import user_handler
from handlers.admin import admin_handler

app = ApplicationBuilder().token(TOKEN).build()

# اضافه کردن هندلرها
app.add_handler(user_handler)
app.add_handler(admin_handler)

if __name__ == "__main__":
    app.run_polling()
