import os
from dotenv import load_dotenv

# Load environment variables from .env file (useful locally)
load_dotenv()

# ===============================
# Telegram Bot Configuration
# ===============================
BOT_TOKEN = os.getenv("BOT_TOKEN")  # من BotFather
CHANNEL_ID = os.getenv("CHANNEL_ID")  # مثال: @channel أو -1001234567890

# ===============================
# API Configuration
# ===============================
API_URL = os.getenv("API_URL", "https://painel.meowssh.shop:5000/test_ssh_public")
STORE_OWNER_ID = int(os.getenv("STORE_OWNER_ID", 1))

# ===============================
# Scheduler Configuration
# ===============================
# الافتراضي: كل 3 ساعات (180 دقيقة)
INTERVAL_MINUTES = int(os.getenv("INTERVAL_MINUTES", 180))
