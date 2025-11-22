# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message
import time
import random

from database.mongo import get_user, update_user

# Cooldown in seconds (24 hours)
DAILY_COOLDOWN = 24 * 60 * 60

# Base reward range
DAILY_MIN = 100
DAILY_MAX = 300


def format_time_left(seconds: int) -> str:
    """Return human-readable time left like '3h 12m 05s'."""
    if seconds < 0:
        seconds = 0

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")

    return " ".join(parts)


def init_daily(bot: Client):
    """
    Initialize the /daily command.
    This will work in all chats (PM, groups, supergroups).
    """

    @bot.on_message(filters.command("daily") & ~filters.edited & ~filters.bot)
    async def daily_handler(_, message: Message):
        user = message.from_user
        if not user:
            return  # safety

        user_id = user.id

        # Load user data from DB
        db_user = get_user(user_id)

        if not db_user:
            await message.reply_text(
                "⚠️ You don't have a profile yet.\n"
                "Use /start first to create your game profile."
            )
            return

        now = int(time.time())
        last_daily = db_user.get("last_daily")

        # Check cooldown
        if last_daily:
            remaining = (last_daily + DAILY_COOLDOWN) - now
            if remaining > 0:
                pretty = format_time_left(remaining)
                await message.reply_text(
                    "⏳ You already claimed your daily reward.\n\n"
                    f"Come back in **{pretty}**."
                )
                return

        # Streak handling
        # - If user claimed within 2× cooldown window, continue streak
        # - Otherwise, reset streak
        streak = db_user.get("daily_streak", 0)

        if last_daily:
            # Time since last claim
            delta = now - last_daily

            if delta <= DAILY_COOLDOWN * 2:
                streak += 1
            else:
                streak = 1
        else:
            streak = 1

        # Main reward
        base_reward = random.randint(DAILY_MIN, DAILY_MAX)

        # Small bonus based on streak (5% per day, max +50%)
        bonus_percent = min(streak * 5, 50)
        bonus = int(base_reward * (bonus_percent / 100))
        total_reward = base_reward + bonus

        # Update coins balance
        current_coins = db_user.get("coins", 0)
        new_balance = current_coins + total_reward

        # Save back to DB
        update_user(
            user_id,
            {
                "coins": new_balance,
                "last_daily": now,
                "daily_streak": streak,
            },
        )

        # Build reply text
        text = (
            f"🎁 **Daily Reward Claimed!**\n\n"
            f"💰 Base reward: **{base_reward}** coins\n"
            f"🔥 Streak bonus: **+{bonus}** coins ({bonus_percent}%)\n"
            f"➕ Total gained: **{total_reward}** coins\n\n"
            f"📅 Current streak: **{streak}** day(s)\n"
            f"🏦 New balance: **{new_balance}** coins"
        )

        await message.reply_text(text)

    print("[loaded] games.daily")
