# filename: games/callbacks.py

from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

# ✅ NEW: use MongoDB instead of data.json
from database.mongo import get_user, update_user

from games.start import get_start_menu, START_TEXT
from games.profile import build_profile_text_for_user, get_profile_markup


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

        markup = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("⬅️ Back", callback_data="back_to_home")]
            ]
        )

        await query.message.edit(text, reply_markup=markup)
        await query.answer()


    # Profile Button (via callback)
    @bot.on_callback_query(filters.regex("^show_profile$"))
    async def show_profile(_, query: CallbackQuery):

        user = get_user(query.from_user.id)        # <-- MongoDB load
        text = build_profile_text_for_user(user, query.from_user.mention)

        await query.message.edit(text, reply_markup=get_profile_markup())
        await query.answer()


    # Back to Home handler
    @bot.on_callback_query(filters.regex("^back_to_home$"))
    async def back_to_home(_, query: CallbackQuery):

        name = query.from_user.first_name if query.from_user else "Player"
        await query.message.edit(
            START_TEXT.format(name=name),
            reply_markup=get_start_menu()
        )
        await query.answer()
