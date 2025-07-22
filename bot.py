import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import Forbidden

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = [os.getenv("CHANNEL_1"), os.getenv("CHANNEL_2")]
PRIVATE_GROUP_LINK = os.getenv("PRIVATE_GROUP_LINK")

# Referal tracking dictionary (in-memory, for testing purposes)
user_referrals = {}  # {user_id: [list of invited user_ids]}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args

    # Referal orqali kelgan bo‘lsa
    if args:
        referrer_id = int(args[0])
        invited_id = user.id

        if invited_id != referrer_id:
            if referrer_id not in user_referrals:
                user_referrals[referrer_id] = set()
            user_referrals[referrer_id].add(invited_id)

    # Foydalanuvchidan kanalga a’zo bo‘lganligini tekshirish
    user_id = user.id
    for channel in CHANNELS:
        try:
            member = await context.bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                await update.message.reply_text(f"Iltimos, {channel} kanaliga a’zo bo‘ling.")
                return
        except Forbidden:
            await update.message.reply_text(f"Botni {channel} kanalga admin qilib qo‘shing.")
            return

    # Agar foydalanuvchi 5 kishi taklif qilgan bo‘lsa
    invited = user_referrals.get(user_id, set())
    if len(invited) >= 5:
        await update.message.reply_text(f"Tabriklaymiz! Siz 5 kishi taklif qildingiz!\nYopiq guruh linki: {PRIVATE_GROUP_LINK}")
    else:
        count = len(invited)
        remaining = 5 - count
        referal_link = f"https://t.me/{context.bot.username}?start={user_id}"
        await update.message.reply_text(
            f"👋 Siz kanalga a’zo bo‘lgansiz.\n"
            f"📨 Endi {remaining} ta do‘stingizni taklif qiling.\n"
            f"📎 Sizning taklif havolangiz: {referal_link}\n"
            f"Taklifingizdan foydalanganlar soni: {count}/5"
        )

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()