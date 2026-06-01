import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEN_API_KEY = os.getenv("GEN_API_KEY")

PHOTO_COST_RUB = 0.30
VIDEO_COST_RUB = 0.30