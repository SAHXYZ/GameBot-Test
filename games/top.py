# filename: games/top.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database_main import db

def _leaderboard_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏆 Coins", callback_data="top_coins"),
                InlineKeyboardButton("💬 Messages", callback_data="top_msgs")
            ]
        ]
    )

def init_top(bot: Client):

    @bot.on_message(filters.command("leaderboard"))
    async def show_menu(_, msg: Message):
        await msg.reply("Choose a leaderboard:", reply_markup=_leaderboard_menu())

    # TOP COINS
    @bot.on_callback_query(filters.regex("^top_coins$"))
    async def top_coins(client, cq: CallbackQuery):

        raw = getattr(db, "_data", {})
        items = [(uid, u.get("coins", 0)) for uid, u in raw.items()]
        items = sorted(items, key=lambda x: x[1], reverse=True)[:10]

        text = "*Top Coins*\n"
        for uid, coins in items:
            text += f"- `{uid}` — {coins} coins\n"

        await cq.message.edit(text)
        await cq.answer()

    # TOP MESSAGES
    @bot.on_callback_query(filters.regex("^top_msgs$"))
    async def top_msgs(client, cq: CallbackQuery):

        raw = getattr(db, "_data", {})
        items = [(uid, u.get("messages", 0)) for uid, u in raw.items()]
        items = sorted(items, key=lambda x: x[1], reverse=True)[:10]

        text = "*Top Messages*\n"
        for uid, msgs in items:
            text += f"- `{uid}` — {msgs} messages\n"

        await cq.message.edit(text)
        await cq.answer()
