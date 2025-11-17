# filename: main.py

from pyrogram import Client
import importlib
import traceback
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client(
    "GameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

def safe_init(module_name: str):
    try:
        mod = importlib.import_module(f"games.{module_name}")
        init_fn = getattr(mod, f"init_{module_name}", None)

        if callable(init_fn):
            init_fn(bot)
            print(f"[loaded] games.{module_name}")
        else:
            print(f"[skipped] games.{module_name} (no init function)")

    except Exception as e:
        print(f"[error] loading games.{module_name}: {e}")
        traceback.print_exc()


# Required modules
required_modules = [
    "start",
    "flip",
    "roll",
    "rob",
    "fight",
    "top",
    "callbacks",   # ensure callbacks is loaded
]

# Optional modules
optional_modules = [
    "profile",
    "work",
    "shop",
    "guess",
]

if __name__ == "__main__":
    for m in required_modules + optional_modules:
        safe_init(m)

    print("Game Bot is running...")
    bot.run()
