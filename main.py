from pyrogram import Client
import importlib
import traceback
from config import API_ID, API_HASH, BOT_TOKEN
from database.mongo import client  # ensure MongoDB connection initializes first


bot = Client(
    "GameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=32
)


def safe_init(module_name: str):
    """
    Loads module like games.start, games.flip, games.mine, etc.
    Calls init_<module> if it exists.
    """

    try:
        module = importlib.import_module(f"games.{module_name}")

        init_fn = getattr(module, f"init_{module_name}", None)

        if callable(init_fn):
            init_fn(bot)
            print(f"[loaded] games.{module_name}")
        else:
            print(f"[skipped] games.{module_name} (no init function)")

    except Exception as e:
        print(f"[ERROR] Failed loading module '{module_name}': {e}")
        traceback.print_exc()


# Modules that MUST load for the bot to function
required_modules = [
    "start", "flip", "roll", "rob",
    "fight", "top", "callbacks"
]

# Modules that are optional OR gameplay features
optional_modules = [
    "profile", "work", "shop",
    "guess", "help", "mine"   # Mining system enabled
]


if __name__ == "__main__":
    print("Initializing GameBot...\n")

    # Load required modules first
    for module in required_modules:
        safe_init(module)

    # Then load optional features
    for module in optional_modules:
        safe_init(module)

    print("\n✔ GameBot is running with MongoDB!")
    bot.run()
