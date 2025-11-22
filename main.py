# File: main.py
from pyrogram import Client
import importlib
import traceback
import time
import os
import database.mongo  # keep it to trigger DB connection
from config import API_ID, API_HASH, BOT_TOKEN

bot = Client(
    "GameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=1
)


def load_all_modules():
    """Auto-detect and load all modules from the /games folder."""
    games_path = os.path.join(os.path.dirname(__file__), "games")

    modules = [
        f[:-3]
        for f in os.listdir(games_path)
        if f.endswith(".py") and f not in ("__init__.py")
    ]

    print(f"🔍 Detecting modules in /games → {len(modules)} found")
    return modules


def safe_init(module_name: str):
    """Initialization manager to prevent duplicate prints & protect bot from failures."""
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

        # retry once
        try:
            mod = importlib.import_module(f"games.{module_name}")
            init_fn = getattr(mod, f"init_{module_name}", None)
            if callable(init_fn):
                init_fn(bot)
                print(f"[loaded after retry] games.{module_name}")
            else:
                print(f"[skipped after retry] games.{module_name}")
        except Exception:
            print(f"[FATAL] failed: {module_name}")
            traceback.print_exc()


if __name__ == "__main__":
    print("Initializing GameBot...")

    modules = load_all_modules()
    for module in modules:
        safe_init(module)

    print("✔ GameBot is running with MongoDB!")
    bot.run()
