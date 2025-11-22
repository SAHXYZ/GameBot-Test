# File: games/callbacks.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import traceback

from database.mongo import get_user
from games.start import get_start_menu, START_TEXT
from games.profile import build_profile_text_for_user, get_profile_markup
from games.daily import claim_daily   # 👈 add this import


async def safe_edit(message, text, markup=None):
    try:
        if markup:
            return await message.edit_text(text, reply_markup=markup)
        else:
            return await message.edit_text(text)
    except Exception:
        return


def init_callbacks(bot: Client):

    # ... your existing start_back, back_to_home, open_profile here ...

    @bot.on_callback_query(filters.regex("^open_daily$"))
    async def cb_open_daily(_, q: CallbackQuery):
        try:
            # directly run daily logic for the user
            await claim_daily(q.from_user.id, q.message)
            await q.answer()
        except Exception:
            traceback.print_exc()
            try:
                await q.answer("⚠️ Unable to open daily.")
            except:
                pass

    # ... your existing open_leaderboard callback, etc. ...

    print("[loaded] games.callbacks")
