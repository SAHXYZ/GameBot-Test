# filename: games/callbacks.py

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
from database_main import db

def init_callbacks(bot: Client):

    # Commands Button
    @bot.on_callback_query(filters.regex("^show_commands$"))
    async def show_commands(_, query: CallbackQuery):

        text = (
            "🎮 **GameBot Commands**\n\n"
            "**General Commands**\n"
            "/start - Show menu\n"
            "/help - Show help menu\n"
            "/profile - Your stats\n"
            "/leaderboard - Top players\n\n"

            "**Game Commands**\n"
            "/flip - Coin flip game\n"
            "/roll - Random dice roll\n"
            "/fight - Fight another user\n"
            "/rob - Rob a user\n"
            "/guess - Word guessing game\n"
            "/work - Earn coins\n"
            "/shop - Purchase items\n"
        )

        await query.message.edit(text)
        await query.answer()


    # Profile Button
    @bot.on_callback_query(filters.regex("^show_profile$"))
    async def show_profile(_, query: CallbackQuery):

        user = db.get_user(query.from_user.id)

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
            f"👤 **Profile of {query.from_user.mention}**\n\n"
            f"💰 **Coins:** `{coins}`\n"
            f"💬 **Messages Sent:** `{messages}`\n\n"
            f"🥊 **Fight Wins:** `{fights}`\n"
            f"🕵️ **Successful Robberies:** `{rob_s}`\n"
            f"🚨 **Failed Robberies:** `{rob_f}`\n\n"
            f"🎖 **Badges:** {badge_text}\n"
            f"🛒 **Inventory:** {inv_text}"
        )

        await query.message.edit(text)
        await query.answer()
