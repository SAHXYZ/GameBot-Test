# File: main.py
from pyrogram import Client
import importlib
import traceback
import time
import database.mongo  # delayed loading to prevent module import blocking
from config import API_ID, API_HASH, BOT_TOKEN


bot = Client(
    "GameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1
)


def safe_init(module_name: str):
    """Imports and initializes modules without duplicate log prints."""
    try:
        mod = importlib.import_module(f"games.{module_name}")
        init_fn = getattr(mod, f"init_{module_name}", None)

        if callable(init_fn):
            init_fn(bot)
            print(f"[loaded] games.{module_name}")
        else:
            print(f"[skipped] games.{module_name}")

    except Exception as e:
        print(f"[ERROR] loading {module_name}: {e}")
        traceback.print_exc()
        print(f"Retrying {module_name} in 1s...")
        time.sleep(1)
        try:
            mod = importlib.import_module(f"games.{module_name}")
            init_fn = getattr(mod, f"init_{module_name}", None)
            if callable(init_fn):
                init_fn(bot)
                print(f"[loaded] games.{module_name}")
            else:
                print(f"[skipped after retry] games.{module_name}")
        except Exception:
            print(f"[FATAL] failed: {module_name}")
            traceback.print_exc()


required_modules = [
    "start",
    "flip",
    "roll",
    "rob",
    "fight",
    "top",
    "help",
    "mine",
    "profile",
    "work",
    "shop",
    "sell",
    "equip",
    "guess",
    "daily",
    "callbacks"
]


if __name__ == "__main__":
    print("Initializing GameBot...")
    for module in required_modules:
        safe_init(module)
    print("✔ GameBot is running with MongoDB!")
    bot.run()
