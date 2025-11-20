from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.mongo import get_user

START_TEXT = (
    "Hᴇʏ {name}\n\n"
    "✧༺━━━༻✧༺━━━༻✧\n"
    "     ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ɢᴀᴍᴇʙᴏᴛ\n"
    "✧༺━━━༻✧༺━━━༻✧\n\n"
    "● ʏᴏᴜ'ᴠᴇ sᴛᴇᴘᴘᴇᴅ ɪɴᴛᴏ ᴀ ᴘʀɪᴍᴇ-ᴛɪᴇʀ ᴅɪɢɪᴛᴀʟ ʀᴇᴀʟᴍ ~\n"
    "ғᴀsᴛᴇʀ. ʙᴏʟᴅᴇʀ. sᴍᴀʀᴛᴇʀ. ᴜɴᴅᴇɴɪᴀʙʟʏ sᴇxɪᴇʀ.\n\n"
    "✦ ᴇᴠᴇʀʏ ᴄʟɪᴄᴋ ɪɢɴɪᴛᴇs ᴘᴏᴡᴇʀ\n"
    "✦ ᴇᴠᴇʀʏ ᴄʜᴏɪᴄᴇ ᴄʀᴀғᴛs ʏᴏᴜʀ ʟᴇɢᴇɴᴅ\n"
    "✦ ᴇᴠᴇʀʏ ᴍᴏᴠᴇ ʟᴇᴀᴠᴇs ᴀ ᴍᴀʀᴋ\n\n"
    "ʟᴇᴠᴇʟ ᴜᴘ. ᴅᴏᴍɪɴᴀᴛᴇ. ᴄᴏɴǫᴜᴇʀ ᴛʜᴇ ɢʀɪᴅ.\n\n"
    "✧༺ ʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ɴᴇxᴛ ᴅᴇsᴛɪɴʏ… ༻✧\n\n"
    "◆ ᴘᴏᴡᴇʀᴇᴅ ʙʏ @PrimordialEmperor ◆"
)

def get_start_menu():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🕹 Commands", callback_data="start_cmds"),
                InlineKeyboardButton("👤 Profile", callback_data="start_profile"),
            ]
        ]
    )

def init_start(bot: Client):

    # ---------------------------------------------------
    # /start in PRIVATE
    # Also handles redirected /start help from group
    # ---------------------------------------------------
    @bot.on_message(filters.command("start") & filters.private)
    async def start_private(_, msg: Message):

        user = msg.from_user
        if not user:
            return

        # Handle redirect: /start help
        args = msg.text.split(maxsplit=1)
        if len(args) > 1 and args[1] == "help":
            from games.help import _help
            return _help(_, msg)

        # Normal start behavior
        get_user(user.id)  # ensure DB entry

        await msg.reply(
            START_TEXT.format(name=user.first_name),
            reply_markup=get_start_menu()
        )

    # ---------------------------------------------------
    # /start in GROUP — show start text directly
    # ---------------------------------------------------
    @bot.on_message(filters.command("start") & ~filters.private)
    async def start_group(_, msg: Message):
        user = msg.from_user
        if not user:
            return

        await msg.reply(
            START_TEXT.format(name=user.first_name),
            reply_markup=get_start_menu()
        )

    # ---------------------------------------------------
    # Callback: Commands menu
    # ---------------------------------------------------
    @bot.on_callback_query(filters.regex("^start_cmds$"))
    async def start_commands(_, q: CallbackQuery):

        await q.message.edit_text(
            "🕹 **Commands Menu**\n\n"
            "📌 **General**\n"
            "/start — Main menu\n"
            "/help — Full help menu\n"
            "/profile — Detailed profile\n"
            "/leaderboard — Top players\n\n"
            "⛏ **Mining System**\n"
            "/mine — Mine ores\n"
            "/sell — Sell ores\n"
            "/tools — Your tools\n"
            "/equip <tool> — Equip tool\n"
            "/repair — Repair tool\n\n"
            "💼 **Economy & Fun**\n"
            "/work — Earn bronze\n"
            "/shop — Buy items\n"
            "/flip — Coin flip\n"
            "/roll — Dice roll\n"
            "/fight — Fight users\n"
            "/rob — Attempt robbery\n"
            "/guess — Word guessing game\n",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
            )
        )
        await q.answer()

    # ---------------------------------------------------
    # Callback: Profile summary
    # ---------------------------------------------------
    @bot.on_callback_query(filters.regex("^start_profile$"))
    async def start_profile(_, q: CallbackQuery):

        user = get_user(q.from_user.id)

        bronze = user.get("bronze", 0)
        items = len(user.get("inventory", {}).get("items", []))
        ores = sum(user.get("inventory", {}).get("ores", {}).values())

        await q.message.edit_text(
            f"👤 **Quick Profile**\n\n"
            f"🥉 Bronze: **{bronze}**\n"
            f"🪨 Ores Collected: **{ores}**\n"
            f"🎒 Items Owned: **{items}**\n\n"
            "Use /profile for the full details.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️ Back", callback_data="start_back")]]
            )
        )
        await q.answer()

    # ---------------------------------------------------
    # Callback: Back → main menu
    # ---------------------------------------------------
    @bot.on_callback_query(filters.regex("^start_back$"))
    async def start_back(_, q: CallbackQuery):

        await q.message.edit_text(
            START_TEXT.format(name=q.from_user.first_name),
            reply_markup=get_start_menu()
        )
        await q.answer()

    print("[loaded] games.start")
