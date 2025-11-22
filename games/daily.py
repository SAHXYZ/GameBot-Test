# File: games/daily.py

import random
import time
import traceback

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from database.mongo import get_user, update_user


def claim_daily(user_id: int) -> str:
    user = get_user(user_id)
    now = int(time.time())
    last = user.get("last_daily")

    if last and (now - last) < 86400:
        remaining = 86400 - (now - last)
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        return f"⏳ You've already claimed today!\nTry again in **{hrs}h {mins}m**."

    reward = random.randint(100, 300)
    user["coins"] = user.get("coins", 0) + reward
    user["last_daily"] = now
    update_user(user_id, user)

    return f"🎁 You earned **{reward} coins** today!"


def init_daily(bot: Client):

    @bot.on_message(filters.command("daily"))
    async def daily_cmd(_, msg: Message):
        try:
            me = await bot.get_me()
            kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎁 Daily Bonus", callback_data="daily_bonus")]]
            )
            await msg.reply_text("Tap below to claim your reward 👇", reply_markup=kb)

        except Exception:
            traceback.print_exc()
            try:
                await msg.reply_text("⚠️ Failed to load daily reward.")
            except:
                pass

    print("[loaded] games.daily")
