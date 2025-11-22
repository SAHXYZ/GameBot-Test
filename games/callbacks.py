# File: GameBot/games/callbacks.py
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery
import traceback

from database.mongo import get_user
from games.start import get_start_menu, START_TEXT
from games.profile import build_profile_text_for_user, get_profile_markup


async def safe_edit(message, text, markup=None):
    try:
        if markup:
            return await message.edit_text(text, reply_markup=markup)
        else:
            return await message.edit_text(text)
    except Exception:
        return


def init_callbacks(bot: Client):

    @bot.on_callback_query(filters.regex("^start_back$"))
    async def start_back(_, q: CallbackQuery):
        try:
            await safe_edit(
                q.message,
                START_TEXT.format(name=q.from_user.first_name),
                get_start_menu()
            )
            await q.answer()
        except Exception:
            traceback.print_exc()
            try:
                await q.answer("⚠️ Error")
            except:
                pass

    @bot.on_callback_query(filters.regex("^back_to_home$"))
    async def cb_back_home(_, q: CallbackQuery):
        try:
            await safe_edit(
                q.message,
                START_TEXT.format(name=q.from_user.first_name),
                get_start_menu()
            )
            await q.answer()
        except Exception:
            traceback.print_exc()
            try:
                await q.answer("⚠️ Error")
            except:
                pass

    @bot.on_callback_query(filters.regex("^open_profile$"))
    async def cb_open_profile(_, q: CallbackQuery):
        try:
            user = get_user(q.from_user.id)
            if not user:
                await q.answer("You have no profile. Use /start")
                return

            mention = getattr(q.from_user, "mention", q.from_user.first_name)
            text = build_profile_text_for_user(user, mention)
            markup = get_profile_markup()

            await safe_edit(q.message, text, markup)
            await q.answer()
        except Exception:
            traceback.print_exc()
            try:
                await q.answer("⚠️ Unable to load profile.")
            except:
                pass

    # 🎁 DAILY BONUS BUTTON
    @bot.on_callback_query(filters.regex("^daily_bonus$"))
    async def daily_bonus_callback(_, query):
        try:
            from games.daily import claim_daily
            user_id = query.from_user.id
            text = claim_daily(user_id)
            await query.answer()
            await query.message.edit_text(text)
        except Exception:
            traceback.print_exc()
            try:
                await query.answer("⚠️ Failed to claim daily bonus.", show_alert=True)
            except:
                pass

    print("[loaded] games.callbacks")



    print("[loaded] games.callbacks")
