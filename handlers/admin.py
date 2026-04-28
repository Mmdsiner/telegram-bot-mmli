from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from database import get_orders, update_order
from config import ADMIN_ID

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    txt = update.message.text

    if txt == "سفارشات":
        orders = await get_orders()
        for o in orders:
            await update.message.reply_text(
                f"{o['id']} | {o['product']} | {o['status']}\n"
                f"/ok_{o['id']} /send_{o['id']}"
            )

    elif txt.startswith("/ok_"):
        oid = int(txt.split("_")[1])
        await update_order(oid, "accepted")
        await update.message.reply_text("تایید شد")

    elif txt.startswith("/send_"):
        context.user_data["send"] = int(txt.split("_")[1])
        await update.message.reply_text("کانفیگ رو بفرست")

    elif "send" in context.user_data:
        oid = context.user_data["send"]
        order = await update_order(oid, "done")

        await context.bot.send_message(order["user_id"], update.message.text)
        await update.message.reply_text("ارسال شد")

        context.user_data.pop("send")

admin_handler = MessageHandler(filters.ALL, admin)
