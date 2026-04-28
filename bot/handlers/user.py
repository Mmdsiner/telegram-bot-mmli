from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, MessageHandler, filters, ConversationHandler
from database import get_settings, create_order

SELECT, RECEIPT = range(2)

def menu():
    return ReplyKeyboardMarkup([["خرید سرویس"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("خوش اومدی", reply_markup=menu())

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("نوع سرویس:", reply_markup=ReplyKeyboardMarkup([["معمولی","ویژه"]], resize_keyboard=True))
    return SELECT

async def select(update: Update, context: ContextTypes.DEFAULT_TYPE):
    settings = await get_settings()
    choice = update.message.text

    price = settings["price_normal"] if choice=="معمولی" else settings["price_vip"]

    context.user_data["product"] = choice
    context.user_data["price"] = price

    await update.message.reply_text(f"""
🧾 فاکتور

{choice}
{price}

شماره کارت:
{settings['card']}

رسید بفرست
""")
    return RECEIPT

async def receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        oid = await create_order(
            update.effective_user.id,
            context.user_data["product"],
            context.user_data["price"]
        )
        await update.message.reply_text("ثبت شد")
        return ConversationHandler.END

user_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("خرید"), buy)],
    states={
        SELECT: [MessageHandler(filters.TEXT, select)],
        RECEIPT: [MessageHandler(filters.ALL, receipt)]
    },
    fallbacks=[]
)
