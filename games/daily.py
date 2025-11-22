# File: games/daily.py
from database.mongo import get_user, update_user
import time
import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def claim_daily(user_id: int) -> str:
    user = get_user(user_id)
    now = int(time.time())

    last = user.get("last_daily")
    if last is not None and (now - last) < 86400:
        remaining = 86400 - (now - last)
        hrs = remaining // 3600
        mins = (remaining % 3600) // 60
        return f"⏳ You already claimed your daily bonus!\nTry again in **{hrs}h {mins}m**."

    reward = random.randint(100, 300)

    user["coins"] = user.get("coins", 0) + reward
    user["last_daily"] = now
    update_user(user_id, user)

    return f"🎁 You claimed **{reward} coins**!"


def init_daily(bot: Client):

    @bot.on_message(filters.command("daily", prefixes="/") | filters.regex("^/daily(@\\w+)?$"))
    @bot.on_edited_message(filters.command("daily", prefixes="/") | filters.regex("^/daily(@\\w+)?$"))
    async def daily_cmd(client, msg):
        chat_type = msg.chat.type

        # Group chat → send button redirecting to DM
        if chat_type in ("supergroup", "group"):
            bot_username = (await client.get_me()).username
            text = (
                "🕹️ **Daily Reward Available!**\n"
                "You must claim it in my DM.\n\n"
                "Click the button below 👇"
            )
            keyboard = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🎁 Claim Daily in DM", url=f"https://t.me/{bot_username}?start=daily")]]
            )
            return await msg.reply(text, reply_markup=keyboard)

        # Private chat → give reward
        try:
            result = claim_daily(msg.from_user.id)
            await msg.reply(result)
        except Exception as e:
            print(e)
            await msg.reply("⚠️ Error in daily reward")
