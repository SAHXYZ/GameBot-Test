# File: games/daily.py
from database.mongo import get_user, update_user
import time
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def claim_daily(user_id: int) -> str:
    """Handles calculation & database update for the daily reward."""
    user = get_user(user_id)
    now = int(time.time())

    last = user.get("last_daily")

    # Check cooldown (24 hours)
    if last is not None and (now - last) < 86400:
        remaining = 86400 - (now - last)
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        return f"⏳ You already claimed your daily bonus!\nTry again in **{hrs}h {mins}m**."

    # Reward range
    reward = random.randint(100, 300)

    # Update user
    user["coins"] = user.get("coins", 0) + reward
    user["last_daily"] = now
    update_user(user_id, user)

    return f"🎁 You claimed **{reward} coins**!"


async def handle_daily(client, msg):
    """Unified handler for both edited and normal messages."""
    chat_type = msg.chat.type

    # Group chat → send button redirecting to DM
    if chat_type in ("supergroup", "group"):
        bot_username = (await client.get_me()).username
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎁 Claim Daily in DM", url=f"https://t.me/{bot_username}?start=daily")]]
        )

    @bot.on_message(filters.command(["daily", "commands"]))
    async def help_cmd(_, msg: Message):
        try:
            group_daily = (
                "🕹️ **Daily Reward Available!**\n"
            "You must claim it in my DM.\n\n"
            "Click the button below 👇"
            btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("🎁 Claim Daily in DM", url=f"https://t.me/{bot_username}?start=daily")]]
            )

            me = await bot.get_me()
            deep_link = f"https://t.me/{me.username}?start=daily"

            group_kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("📘 Help & Commands", url=deep_link)]]
            )

            # --------- FINAL, BULLETPROOF PRIVATE DETECTION ----------
            chat_type = str(msg.chat.type).lower()
            PRIVATE = ("private" in chat_type)


        except Exception:
            traceback.print_exc()
            try:
                await msg.reply_text("⚠️ Failed to load daily menu.")
            except:
                pass

    # /daily command
    @bot.on_message(filters.command("daily"))
    async def daily_cmd_message(client, msg):
        await handle_daily(client, msg)

    # Edited /daily
    @bot.on_edited_message(filters.regex(r"^/daily(@[\w_]+)?"))
    async def daily_cmd_edit(client, msg):
        await handle_daily(client, msg)

    print("[loaded] games.daily")
