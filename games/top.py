# filename: games/top.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database_main import db

def _leaderboard_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('🏆 Coins', callback_data='top_coins'),
                InlineKeyboardButton('💬 Messages', callback_data='top_msgs')
            ],
        ]
    )

def init_top(bot: Client):

    @bot.on_message(filters.command('leaderboard'))
    async def show_menu(_, msg: Message):
        if not msg.from_user:
            return
        await msg.reply('Choose a leaderboard:', reply_markup=_leaderboard_menu())

    # STRICT CALLBACK HANDLER — ONLY MATCHES leaderboard callbacks
    @bot.on_callback_query(filters.create(lambda _, q: q.data in ["top_coins", "top_msgs"]))
    async def cb_top(client, cq: CallbackQuery):

        raw = getattr(db, '_data', {})
        
        if cq.data == "top_coins":
            items = [(uid, u.get('coins', 0)) for uid, u in raw.items()]
            items = sorted(items, key=lambda x: x[1], reverse=True)[:10]
            text = '*Top Coins*\n'
            for uid, coins in items:
                text += f'- `{uid}` — {coins} coins\n'

        elif cq.data == "top_msgs":
            items = [(uid, u.get('messages', 0)) for uid, u in raw.items()]
            items = sorted(items, key=lambda x: x[1], reverse=True)[:10]
            text = '*Top Messages*\n'
            for uid, msgs in items:
                text += f'- `{uid}` — {msgs} messages\n'

        await cq.message.edit(text)
        await cq.answer()
