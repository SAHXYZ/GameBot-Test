# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery
import time, random
from database.mongo import get_user, update_user

DAILY_COOLDOWN = 24 * 60 * 60
DAILY_MIN = 100
DAILY_MAX = 300


def format_time_left(seconds: int) -> str:
    if seconds < 0: seconds = 0
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    out = []
    if h: out.append(f"{h}h")
    if m: out.append(f"{m}m")
    if s or not out: out.append(f"{s}s")
    return " ".join(out)


async def give_daily(bot, user_id: int, reply_target):
    user = get_user(user_id)
    if not user:
        await reply_target.reply_text("⚠️ You don't have a profile yet.\nUse /start.")
        return

    now = int(time.time())
    last = user.get("last_daily")

    if last:
        remaining = (last + DAILY_COOLDOWN) - now
        if remaining > 0:
            await reply_target.reply_text(
                f"⏳ You already claimed today.\n"
                f"Next reward in **{format_time_left(remaining)}**."
            )
            return

    streak = user.get("daily_streak", 0)
    if last and now - last <= DAILY_COOLDOWN * 2:
        streak += 1
    else:
        streak = 1

    base = random.randint(DAILY_MIN, DAILY_MAX)
    bonus_percent = min(streak * 5, 50)
    bonus = int(base * bonus_percent / 100)
    total = base + bonus
    new_balance = user.get("coins", 0) + total

    update_user(
        user_id,
        {"coins": new_balance, "last_daily": now, "daily_streak": streak},
    )

    await reply_target.reply_text(
        f"🎁 **Daily Reward Claimed!**\n\n"
        f"💰 Base reward: **{base}**\n"
        f"🔥 Streak bonus: **+{bonus}** ({bonus_percent}%)\n"
        f"🏦 Total earned: **{total}** coins\n\n"
        f"📅 Streak: **{streak}** days\n"
        f"💼 Balance: **{new_balance}** coins"
    )


def init_daily(bot: Client):

    # UNIVERSAL /daily detector — works for any formatting & any language keyboard
    @bot.on_message(filters.text & filters.regex(r"(?i).*\/daily.*"))
    async def daily_cmd(_, msg: Message):
        await give_daily(bot, msg.from_user.id, msg)

    # Callback button for Daily Bonus
    @bot.on_callback_query(filters.regex("^open_daily$"))
    async def daily_cb(_, q: CallbackQuery):
        await give_daily(bot, q.from_user.id, q.message)
        await q.answer()

    print("[loaded] games.daily")
