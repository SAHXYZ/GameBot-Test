# filename: games/profile.py

from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db

def init_profile(bot: Client):

    @bot.on_message(filters.command("profile"))
    async def profile(_, msg: Message):

        if not msg.from_user:
            return

        user = db.get_user(msg.from_user.id)

        coins = user.get("coins", 0)
        messages = user.get("messages", 0)
        fights = user.get("fight_wins", 0)
        rob_s = user.get("rob_success", 0)
        rob_f = user.get("rob_fail", 0)
        badges = user.get("badges", [])
        inventory = user.get("inventory", [])

        badge_text = " ".join(badges) if badges else "None"
        inv_text = ", ".join(inventory) if inventory else "No items"

        text = (
            f"👤 **Profile of {msg.from_user.mention}**\n\n"
            f"💰 **Coins:** `{coins}`\n"
            f"💬 **Messages Sent:** `{messages}`\n\n"
            f"🥊 **Fight Wins:** `{fights}`\n"
            f"🕵️ **Successful Robberies:** `{rob_s}`\n"
            f"🚨 **Failed Robberies:** `{rob_f}`\n\n"
            f"🎖 **Badges:** {badge_text}\n"
            f"🛒 **Inventory:** {inv_text}"
        )

        await msg.reply(text)
