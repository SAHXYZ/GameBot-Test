# File: games/daily.py
from database.mongo import db
import time
import random
from pyrogram import Client, filters

def claim_daily(user_id: int) -> str:
    user = db.get_user(user_id)
    now = int(time.time())

    last_daily = user.get("last_daily", 0) or 0  # fail-safe fix

    if now - last_daily < 86400:
        remaining = 86400 - (now - last_daily)
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        return f"⏳ You already claimed your daily bonus!\nTry again in **{hrs}h {mins}m**."

    reward = random.randint(100, 300)
    user["coins"] = user.get("coins", 0) + reward
    user["last_daily"] = now

    db.update_user(user_id, user)
    return f"🎁 You claimed **{reward} coins**!"

def init_daily(bot: Client):
    @bot.on_message(filters.command("daily"))
    async def daily_cmd(_, msg):
        result = claim_daily(msg.from_user.id)
        await msg.reply(result)
