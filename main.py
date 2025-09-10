import asyncio
import requests
from telegram import Bot
from telegram.error import TelegramError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from config import BOT_TOKEN, CHANNEL_ID, API_URL, STORE_OWNER_ID, INTERVAL_MINUTES

# Check if BOT_TOKEN and CHANNEL_ID are set
if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("BOT_TOKEN and CHANNEL_ID must be set in .env file")

# Store the last message ID for deletion
last_message_id = None

async def fetch_ssh_account():
    """Fetch SSH account from the API."""
    try:
        response = requests.post(API_URL, json={"store_owner_id": STORE_OWNER_ID})
        response.raise_for_status()
        data = response.json()
        usuario = data.get("Usuario") or data.get("usuario", "N/A")
        senha = data.get("Senha") or data.get("senha", "N/A")
        ip = data.get("IP", "N/A")
        expiracao = data.get("Expiracao", "N/A")
        limite = data.get("limite", "N/A")
        
        message = f"🔐 حساب SSH جديد:\n\n👤 المستخدم: `{usuario}`\n🔑 كلمة المرور: `{senha}`\n⏰ انتهاء: {expiracao}"
        return message
    except requests.RequestException as e:
        return f"❌ خطأ في جلب الحساب: {str(e)}"

async def send_ssh_to_channel():
    """Send SSH account to the Telegram channel and delete previous message."""
    global last_message_id
    bot = Bot(token=BOT_TOKEN)
    
    # Delete previous message if exists
    if last_message_id:
        try:
            await bot.delete_message(chat_id=CHANNEL_ID, message_id=last_message_id)
            print("🗑️ تم حذف الرسالة السابقة.")
        except TelegramError as e:
            print(f"⚠️ لم يتم حذف الرسالة السابقة: {str(e)}")
    
    # Send new message
    message = await fetch_ssh_account()
    try:
        sent_message = await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown")
        last_message_id = sent_message.message_id
        print("✅ تم إرسال الحساب الجديد إلى القناة مع أزرار النسخ.")
    except TelegramError as e:
        print(f"❌ خطأ في إرسال الرسالة: {str(e)}")


async def main():
    """Main function to start the scheduler with 60-minute interval."""
    # Send immediately on startup
    await send_ssh_to_channel()
    
    # Then schedule it every 60 seconds
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_ssh_to_channel, 'interval', seconds=10800, id='ssh_job')
    scheduler.start()
    
    print(f"🚀 البوت يعمل... سيرسل حساب كل 60 ثانية إلى {CHANNEL_ID}")
    
    # Keep the bot running
    try:
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        print("⏹️ تم إيقاف البوت.")
        scheduler.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
