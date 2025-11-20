from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.mongo import get_user
from games.start import get_start_menu, START_TEXT
from games.profile import build_profile_text_for_user, get_profile_markup


def safe_edit(message, text, markup=None):
    """Safely edit message without crashing."""
    try:
        if markup:
            return message.edit(text, reply_markup=markup)
        return message.edit(text)
    except:
        return  # ignore message-not-modified or deleted errors


def init_callbacks(bot: Client):

    # -----------------------------
    # SHOW COMMANDS
    # -----------------------------
    @bot.on_callback_query(filters.regex("^show_commands$"))
    async def show_commands(_, query: CallbackQuery):

        text = (
            "🎮 **GameBot Commands**\n\n"
            "**General Commands**\n"
            "/start - Show main menu\n"
            "/help - Help menu\n"
            "/profile - Your profile\n"
            "/leaderboard - Top players\n\n"

            "**Mining System**\n"
            "/mine - Mine ores\n"
            "/sell - Sell ores\n"
            "/tools - View tools\n"
            "/equip <tool> - Equip tool\n"
            "/repair - Repair tool\n\n"

            "**Economy**\n"
            "/work - Earn coins\n"
            "/shop - Buy items\n"
            "/buy <num> - Purchase\n\n"

            "**Games**\n"
            "/flip - Coin flip\n"
            "/roll - Dice roll\n"
            "/fight - Fight a user\n"
            "/rob - Rob a user\n"
            "/guess - Guess game\n"
        )

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_home")]]
        )

        safe_edit(query.message, text, markup)
        await query.answer()


    # -----------------------------
    # PROFILE BUTTON
    # -----------------------------
    @bot.on_callback_query(filters.regex("^show_profile$"))
    async def show_profile(_, query: CallbackQuery):

        user = get_user(query.from_user.id)
        text = build_profile_text_for_user(user, query.from_user.mention)

        safe_edit(query.message, text, get_profile_markup())
        await query.answer()


    # -----------------------------
    # BACK TO HOME
    # -----------------------------
    @bot.on_callback_query(filters.regex("^back_to_home$"))
    async def back_to_home(_, query: CallbackQuery):

        name = query.from_user.first_name if query.from_user else "Player"
        safe_edit(query.message, START_TEXT.format(name=name), get_start_menu())

        await query.answer()
