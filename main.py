# File: GameBot/main.py
from pyrogram import Client
import importlib
import traceback
from config import API_ID, API_HASH, BOT_TOKEN
from database.mongo import client   # ensure MongoDB loads first


bot = Client(
    "GameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=32
)


def safe_init(module_name: str):
    """
    Simple and stable loader — import ONLY from games.<module>.
    No fallback, no alternate packages, no circular import triggers.
    """
    try:
        mod = importlib.import_module(f"games.{module_name}")
        init_fn = getattr(mod, f"init_{module_name}", None)

        if callable(init_fn):
            init_fn(bot)
            print(f"[loaded] games.{module_name}")
        else:
            print(f"[skipped] games.{module_name} (no init)")
    except Exception as e:
        print(f"[ERROR] Failed to load {module_name}: {e}")
        traceback.print_exc()


# Load modules
required_modules = [
    "start", "flip", "roll", "rob",
    "fight", "top", "callbacks"
]

optional_modules = [
    "profile", "work", "shop",
    "guess", "help", "mine"
]


if __name__ == "__main__":
    print("Initializing GameBot...\n")

    for module in required_modules + optional_modules:
        safe_init(module)

    print("\n✔ GameBot initialized. Starting client...")
    bot.run()
