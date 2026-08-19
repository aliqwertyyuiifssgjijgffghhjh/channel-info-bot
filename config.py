import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

if not BOT_TOKEN:
    print(
        "WARNING: BOT_TOKEN is not configured. "
        "Set the BOT_TOKEN environment variable."
    )
