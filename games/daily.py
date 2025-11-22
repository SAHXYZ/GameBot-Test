# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
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


async def claim_daily_and_reply(bot, user_id, reply_target):
    """Handles daily logic and sends reply to a message OR callback."""
    db_user = get_user(user_id)
    if not db_user:
        await reply_target.reply_text("⚠️ You don't have a profile yet.\nUse /start to create one.")
        return

    now = int(time.time())
    last_daily = db_user.get("last_daily")

    if last_daily:
        remaining = (last_daily + DAILY_COOLDOWN) - now
        if remaining > 0:
            await reply_target.reply_text(
                f"⏳ You already claimed today.\n"
                f"Next reward in **{format_time_left(remaining)}**."
            )
            return

    streak = db_user.get("daily_streak", 0)
    if last_daily and now - last_daily <= DAILY_COOLDOWN * 2:
        streak += 1
    else:
        streak = 1

    base = random.randint(DAILY_MIN, DAILY_MAX)
    bonus_pct = min(streak * 5, 50)
    bonus = int(base * bonus_pct / 100)
    total = base + bonus
    new_balance = db_user.get("coins", 0) + total

    update_user(
        user_id,
        {
            "coins": new_balance,
            "last_daily": now,
            "daily_streak": streak,
        },
    )

    await reply_target.reply_text(
        f"🎁 **Daily Reward Claimed!**\n\n"
        f"💰 Base reward: **{base}** coins\n"
        f"🔥 Streak bonus: **+{bonus}** coins ({bonus_pct}%)\n"
        f"🏦 Total gained: **{total}** coins\n\n"
        f"📅 Streak: **{streak}** days\n"
        f"💼 New balance: **{new_balance}** coins"
    )


def init_daily(bot: Client):

    # user manually types /daily
   @bot.on_message((filters.command("daily") | filters.regex(r"(?i)^[/!.]daily\b")))
    async def daily_handler(_, message: Message):
        await claim_daily_and_reply(bot, message.from_user.id, message)

    # user clicks Daily Bonus button (callback)
    @bot.on_callback_query(filters.regex("^open_daily$"))
    async def callback_daily(_, q: CallbackQuery):
        await claim_daily_and_reply(bot, q.from_user.id, q.message)
        await q.answer()

    print("[loaded] games.daily")
