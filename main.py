import asyncio
import json
import os
import requests
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN, CHANNEL_ID, API_URL, STORE_OWNER_ID

# ملف تخزين آخر ID للرسالة
LAST_MSG_FILE = "last_message.json"

def save_last_message_id(message_id: int):
    with open(LAST_MSG_FILE, "w") as f:
        json.dump({"last_message_id": message_id}, f)

def load_last_message_id():
    if os.path.exists(LAST_MSG_FILE):
        with open(LAST_MSG_FILE, "r") as f:
            try:
                data = json.load(f)
                return data.get("last_message_id")
            except json.JSONDecodeError:
                return None
    return None

async def fetch_ssh_account():
    """جلب حساب SSH من API."""
    try:
        response = requests.post(API_URL, json={"store_owner_id": STORE_OWNER_ID})
        response.raise_for_status()
        data = response.json()
        usuario = data.get("Usuario") or data.get("usuario")
        senha = data.get("Senha") or data.get("senha")
        expiracao = data.get("Expiracao")

        if not usuario or not senha:
            return None, "⚠️ لم يتم استرجاع بيانات الحساب من API."

        message = (
            "🔐 **حساب SSH جديد**\n\n"
            f"👤 المستخدم: `{usuario}`\n"
            f"🔑 كلمة المرور: `{senha}`\n"
            f"⏰ انتهاء: {expiracao or 'N/A'}"
        )

        buttons = [
            [InlineKeyboardButton("👤 نسخ المستخدم", callback_data=f"copy:{usuario}")],
            [InlineKeyboardButton("🔑 نسخ كلمة المرور", callback_data=f"copy:{senha}")]
        ]
        return InlineKeyboardMarkup(buttons), message
    except requests.RequestException as e:
        return None, f"❌ خطأ في جلب الحساب: {str(e)}"

async def send_ssh_to_channel():
    """إرسال حساب SSH جديد مع تثبيت الرسالة وحذف القديم."""
    bot = Bot(token=BOT_TOKEN)

    # فك تثبيت الرسالة القديمة + حذفها
    last_message_id = load_last_message_id()
    if last_message_id:
        try:
            await bot.unpin_chat_message(chat_id=CHANNEL_ID, message_id=last_message_id)
            print("📌 تم فك تثبيت الرسالة السابقة.")
        except TelegramError:
            pass
        try:
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=last_message_id)
            print("🗑️ تم حذف الرسالة السابقة.")
        except TelegramError:
            pass

    # جلب الحساب الجديد
    keyboard, message = await fetch_ssh_account()

    # إرسال وتثبيت الرسالة الجديدة
    try:
        sent_message = await bot.send_message(
            chat_id=CHANNEL_ID,
            text=message,
            parse_mode="Markdown",
            reply_markup=keyboard if keyboard else None
        )
        save_last_message_id(sent_message.message_id)

        await bot.pin_chat_message(chat_id=CHANNEL_ID, message_id=sent_message.message_id, disable_notification=True)
        print("📌 تم تثبيت الرسالة الجديدة.")

    except TelegramError as e:
        print(f"❌ خطأ في إرسال الرسالة: {str(e)}")

async def main():
    await send_ssh_to_channel()

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_ssh_to_channel, 'interval', hours=3, id='ssh_job')
    scheduler.start()

    print(f"🚀 البوت يعمل... سيرسل حساب جديد كل 3 ساعات إلى {CHANNEL_ID}")

    try:
        await asyncio.Future()
    except KeyboardInterrupt:
        print("⏹️ تم إيقاف البوت.")
        scheduler.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
