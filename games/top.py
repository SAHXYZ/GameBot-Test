# filename: games/top.py

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)
from database_main import db
from utils.coins import total_bronze_value


# ------------------------------
# Leaderboard Buttons
# ------------------------------
def leaderboard_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏆 Top Wealth", callback_data="top_coins"),
                InlineKeyboardButton("💬 Top Messages", callback_data="top_msgs")
            ]
        ]
    )

def back_button():
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data="lb_back")]]
    )


# ------------------------------
# INIT FUNCTION
# ------------------------------
def init_top(bot: Client):

    @bot.on_message(filters.command("leaderboard"))
    async def show_menu(_, msg: Message):
        await msg.reply("📊 **Choose a leaderboard:**", reply_markup=leaderboard_menu())

    # ------------------------------
    # TOP COINS
    # ------------------------------
    @bot.on_callback_query(filters.regex("^top_coins$"))
    async def top_coins(client, cq: CallbackQuery):

        raw = getattr(db, "_data", {})

        items = []
        for uid, u in raw.items():
            total = total_bronze_value(u)
            items.append((uid, total, u))

        items = sorted(items, key=lambda x: x[1], reverse=True)[:10]

        text = "🏆 **Top Wealth Leaderboard**\n\n"

        rank = 1
        for uid, value, data in items:
            # Fetch username properly
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except:
                name = f"User {uid}"

            # Get coin breakdown
            bg = data.get("black_gold", 0)
            pt = data.get("platinum", 0)
            gd = data.get("gold", 0)
            sv = data.get("silver", 0)
            bz = data.get("bronze", 0)

            text += (
                f"**{rank}. {name}**\n"
                f"🎖 {bg} | 🏅 {pt} | 🥇 {gd} | 🥈 {sv} | 🥉 {bz}\n"
                f"💰 **Total Value:** `{value}`\n\n"
            )
            rank += 1

        await cq.message.edit(text, reply_markup=back_button())
        await cq.answer()

    # ------------------------------
    # TOP MESSAGES
    # ------------------------------
    @bot.on_callback_query(filters.regex("^top_msgs$"))
    async def top_msgs(client, cq: CallbackQuery):

        raw = getattr(db, "_data", {})

        items = [(uid, u.get("messages", 0)) for uid, u in raw.items()]
        items = sorted(items, key=lambda x: x[1], reverse=True)[:10]

        text = "💬 **Top Message Senders**\n\n"

        rank = 1
        for uid, messages in items:
            try:
                user = await client.get_users(int(uid))
                name = user.first_name
            except:
                name = f"User {uid}"

            text += f"**{rank}. {name}** — `{messages}` messages\n"
            rank += 1

        await cq.message.edit(text, reply_markup=back_button())
        await cq.answer()

    # ------------------------------
    # BACK BUTTON HANDLER
    # ------------------------------
    @bot.on_callback_query(filters.regex("^lb_back$"))
    async def leaderboard_back(_, cq: CallbackQuery):
        await cq.message.edit("📊 **Choose a leaderboard:**", reply_markup=leaderboard_menu())
        await cq.answer()
