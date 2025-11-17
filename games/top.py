# filename: games/top.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database_main import db

def _leaderboard_menu():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton('🏆 Coins', callback_data='top_coins'),
             InlineKeyboardButton('💬 Messages', callback_data='top_msgs')],
        ]
    )

def init_top(bot: Client):
    @bot.on_message(filters.command('leaderboard'))
    async def show_menu(_, msg: Message):
        if not msg.from_user:
            return
        await msg.reply('Choose a leaderboard:', reply_markup=_leaderboard_menu())

    @bot.on_callback_query()
    async def cb_top(client, cq: CallbackQuery):
        data = cq.data or ''
        all_data = db._load() if hasattr(db, '_load') else {}  # fallback: direct access
        # db.get_user returns defaults but we need raw mapping; try to access db._data
        try:
            raw = getattr(db, '_data', {})
            items = [(uid, u.get('coins',0)) for uid,u in raw.items()]
        except Exception:
            items = []
        items = sorted(items, key=lambda x: x[1], reverse=True)[:10]
        text = '*Top Coins*\n'
        for uid, coins in items:
            text += f'- `{uid}` — {coins} coins\n'
        try:
            await cq.message.edit(text)
            await cq.answer()
        except:
            await cq.answer('Could not update message.')
