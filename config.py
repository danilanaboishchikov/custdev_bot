import os
from pathlib import Path

import telebot

BASE_DIR = Path(__file__).resolve().parent


def load_env_file(path):
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(name, value)


load_env_file(BASE_DIR / ".env")

DEMO_MODE = os.getenv("DEMO_MODE", "0") == "1"
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or "0:DEMO_TOKEN_REPLACE_ME"
PAY_TOKEN = os.getenv("YOOMONEY_TOKEN", "")
YOOMONEY_RECEIVER = os.getenv("YOOMONEY_RECEIVER", "")
ARBITRASH_CHAT_URL = os.getenv("ARBITRATION_CHAT_URL", "")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0") or 0)


def parse_admin_ids(value):
    return [int(item.strip()) for item in value.split(",") if item.strip().lstrip("-").isdigit()]


ADMINS = parse_admin_ids(os.getenv("ADMIN_IDS", ""))

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="html")
