from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from database.mongo import get_user
from games.start import get_start_menu, START_TEXT
from games.profile import build_profile_text_for_user, get_profile_markup


def safe_edit(message, text, markup=None):
    try:
        if markup:
            return message.edit(text, reply_markup=markup)
        return message.edit(text)
    except:
        return


def init_callbacks(bot: Client):

    # ===============================
    # /start MENU CALLBACKS
    # ===============================

    @bot.on_callback_query(filters.regex("^start_cmds$"))
    async def cb_start_cmds(_, q: CallbackQuery):

        text = (
            "🕹 **Commands Menu**\n\n"
            "📌 **General**\n"
            "/start — Main menu\n"
            "/help — Full help\n"
            "/profile — Full profile\n"
            "/leaderboard — Top players\n\n"
            "⛏ **Mining System**\n"
            "/mine — Mine ores\n"
            "/sell — Sell ores\n"
            "/tools — Tools\n"
            "/equip <tool> — Equip tool\n"
            "/repair — Repair tool\n\n"
            "💼 **Economy**\n"
            "/work — Earn bronze\n"
            "/shop — Buy items\n"
            "/buy <num> — Purchase items\n\n"
            "🎮 **Fun Games**\n"
            "/flip — Coin toss\n"
            "/roll — Dice\n"
            "/fight — Fight users\n"
            "/rob — Rob users\n"
            "/guess — Word guessing\n"
        )

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
        )

        safe_edit(q.message, text, markup)
        await q.answer()


    @bot.on_callback_query(filters.regex("^start_profile$"))
    async def cb_start_profile(_, q: CallbackQuery):

        user = get_user(q.from_user.id)

        ores = sum(user.get("inventory", {}).get("ores", {}).values())
        items = len(user.get("inventory", {}).get("items", []))

        text = (
            f"👤 **Quick Profile**\n\n"
            f"🥉 Bronze: **{user.get('bronze', 0)}**\n"
            f"🪨 Ores: **{ores}**\n"
            f"🎒 Items: **{items}**\n\n"
            "Use /profile for full details."
        )

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
        )

        safe_edit(q.message, text, markup)
        await q.answer()


    @bot.on_callback_query(filters.regex("^start_back$"))
    async def cb_start_back(_, q: CallbackQuery):

        safe_edit(
            q.message,
            START_TEXT.format(name=q.from_user.first_name),
            get_start_menu()
        )
        await q.answer()


    # ============================================
    # LEGACY FALLBACK (FOR OLD MODULE BUTTONS)
    # ============================================

    @bot.on_callback_query(filters.regex("^show_commands$"))
    async def cb_old_commands(_, q: CallbackQuery):

        text = (
            "🎮 **GameBot Commands**\n\n"
            "/start — Main menu\n"
            "/help — Help\n"
            "/profile — Profile\n"
            "/leaderboard — Top users\n\n"
            "⛏ /mine /sell /tools /equip /repair\n"
            "💼 /work /shop /flip /roll\n"
            "🥊 /fight /rob /guess"
        )

        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Back", callback_data="back_to_home")]]
        )

        safe_edit(q.message, text, markup)
        await q.answer()


    @bot.on_callback_query(filters.regex("^show_profile$"))
    async def cb_old_profile(_, q: CallbackQuery):

        user = get_user(q.from_user.id)
        text = build_profile_text_for_user(user, q.from_user.mention)

        safe_edit(q.message, text, get_profile_markup())
        await q.answer()


    @bot.on_callback_query(filters.regex("^back_to_home$"))
    async def cb_back_home(_, q: CallbackQuery):

        safe_edit(
            q.message,
            START_TEXT.format(name=q.from_user.first_name),
            get_start_menu()
        )
        await q.answer()


    print("[loaded] games.callbacks")
