# File: GameBot/GameBot/main.py
from pyrogram import Client
import importlib
import traceback
import sys
import os
from config import API_ID, API_HASH, BOT_TOKEN
from database.mongo import client  # ensure MongoDB initializes first

# Ensure project root is on sys.path so "games.*" imports work whether run as script or package
_this_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.dirname(_this_dir)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

bot = Client(
    "GameBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    workers=32
)

def safe_init(module_name: str):
    """
    Load game modules safely.
    Tries multiple qualified import names to be resilient to how the bot is started.
    """
    tried = []
    candidates = [f"games.{module_name}"]
    top_pkg = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
    candidates.append(f"{top_pkg}.games.{module_name}")

    for qualname in candidates:
        try:
            tried.append(qualname)
            module = importlib.import_module(qualname)
            init_fn = getattr(module, f"init_{module_name}", None)

            if callable(init_fn):
                init_fn(bot)
                print(f"[loaded] {qualname}")
            else:
                print(f"[skipped] {qualname} (no init function)")
            return
        except Exception as e:
            print(f"[DEBUG] Import attempt failed for '{qualname}': {e}")
            # continue trying other candidates

    print(f"[ERROR] Failed loading module '{module_name}'. Tried: {tried}")
    traceback.print_exc()

required_modules = [
    "start", "flip", "roll", "rob",
    "fight", "top"
]
optional_modules = [
    "profile", "work", "shop",
    "guess", "help", "mine"
]

if __name__ == "__main__":
    print("Initializing GameBot...\n")

    for module in required_modules:
        safe_init(module)

    for module in optional_modules:
        safe_init(module)

    # Load callbacks LAST
    safe_init("callbacks")

    print("\n✔ GameBot is running with MongoDB!")
    bot.run()
