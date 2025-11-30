import logging
import requests
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)

BOT_TOKEN = "8285902013:AAFGyPIZcYTAe8d3yboCJsKdv32RypSYhUA"

# YOUR CHANNELS
CHANNEL_1 = "@Xploitfamily"
CHANNEL_2 = "@xploit_tech"

API_URL = "https://rc-s5ts.onrender.com/fetch?key=R4HULxTRUSTED&aadhaar="

logging.basicConfig(level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Check subscription
    if not await is_joined(context, user_id):
        keyboard = [
            [InlineKeyboardButton("Join Channel 1", url=f"https://t.me/{CHANNEL_1.replace('@','')}")],
            [InlineKeyboardButton("Join Channel 2", url=f"https://t.me/{CHANNEL_2.replace('@','')}")],
            [InlineKeyboardButton("✔ I Have Joined", callback_data="check_sub")]
        ]
        await update.message.reply_text(
            "🚫 *You must join both channels to use this bot!*",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "👋 Welcome dear!\n\nSend *12-digit Aadhaar number* to fetch details.",
        parse_mode="Markdown"
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_sub":
        user_id = query.from_user.id
        if not await is_joined(context, user_id):
            await query.edit_message_text("❌ You still haven't joined both channels!")
            return

        await query.edit_message_text("✅ Verified!\n\nNow send Aadhaar number.")


async def handle_aadhaar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    aadhaar = update.message.text.strip()

    if not aadhaar.isdigit() or len(aadhaar) != 12:
        await update.message.reply_text("❌ Invalid Aadhaar! Send 12 digit number.")
        return

    url = API_URL + aadhaar
    msg = await update.message.reply_text("🔍 Fetching data, wait...")

    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except:
        await msg.edit_text("⚠ API Error!")
        return

    if "homeStateName" not in data:
        await msg.edit_text("❌ No record found!")
        return

    # formatted reply
    text = f"""
🟪 *Aadhaar Info Found*

🏛 State: *{data['homeStateName']}*
🏙 District: *{data['homeDistName']}*
🏠 Scheme: *{data['schemeName']}*
📍 FPS ID: *{data['fpsId']}*

👨‍👩‍👦 *Family Members:*
"""

    for m in data['memberDetailsList']:
        text += f"- *{m['memberName']}* ({m['releationship_name']})\n"

    await msg.edit_text(text, parse_mode="Markdown")


# ✅ FIXED VERSION — owner/admin/member all allowed
async def is_joined(context, user_id):
    try:
        member1 = await context.bot.get_chat_member(CHANNEL_1, user_id)
        member2 = await context.bot.get_chat_member(CHANNEL_2, user_id)

        valid = ["member", "administrator", "creator"]

        return member1.status in valid and member2.status in valid

    except Exception as e:
        print("Error:", e)
        return False


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_aadhaar))

    print("BOT STARTED...")
    app.run_polling()


if __name__ == "__main__":
    main()