# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message
import time
import random

from database.mongo import get_user, update_user

DAILY_COOLDOWN = 24 * 60 * 60
DAILY_MIN = 100
DAILY_MAX = 300


def format_time_left(seconds: int) -> str:
    if seconds < 0:
        seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    parts = []
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    if s or not parts: parts.append(f"{s}s")
    return " ".join(parts)


def init_daily(bot: Client):

    # FINAL FIX → allow bot-generated daily calls from callback button
    @bot.on_message(filters.command("daily"))
    async def daily_handler(_, message: Message):
        user = message.from_user
        if not user:
            return

        user_id = user.id
        db_user = get_user(user_id)

        if not db_user:
            await message.reply_text(
                "⚠️ You don't have a profile yet.\nUse /start to create one."
            )
            return

        now = int(time.time())
        last_daily = db_user.get("last_daily")

        # Cooldown check
        if last_daily:
            remaining = (last_daily + DAILY_COOLDOWN) - now
            if remaining > 0:
                await message.reply_text(
                    f"⏳ You already claimed today.\n"
                    f"Next reward in **{format_time_left(remaining)}**."
                )
                return

        # Streak logic
        streak = db_user.get("daily_streak", 0)
        if last_daily and now - last_daily <= DAILY_COOLDOWN * 2:
            streak += 1
        else:
            streak = 1

        # Rewards
        base = random.randint(DAILY_MIN, DAILY_MAX)
        bonus_pct = min(streak * 5, 50)
        bonus = int(base * bonus_pct / 100)
        total = base + bonus

        new_balance = db_user.get("coins", 0) + total

        # Save database
        update_user(
            user_id,
            {
                "coins": new_balance,
                "last_daily": now,
                "daily_streak": streak,
            },
        )

        # Final reply
        await message.reply_text(
            f"🎁 **Daily Reward Claimed!**\n\n"
            f"💰 Base reward: **{base}** coins\n"
            f"🔥 Streak bonus: **+{bonus}** coins ({bonus_pct}%)\n"
            f"🏦 Total gained: **{total}** coins\n\n"
            f"📅 Streak: **{streak}** days\n"
            f"💼 New balance: **{new_balance}** coins"
        )

    print("[loaded] games.daily")
