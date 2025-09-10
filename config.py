import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration for the Telegram Bot
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Replace with your bot token from BotFather
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Replace with your channel ID (e.g., @channel or -1001234567890)

# API Configuration
API_URL = "https://painel.meowssh.shop:5000/test_ssh_public"
STORE_OWNER_ID = 1

# Scheduler Configuration
INTERVAL_MINUTES = 10
