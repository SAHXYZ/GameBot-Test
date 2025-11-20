# games/help.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


HELP_TEXT = (
    "🎮 **GameBot Help Menu**\n\n"
    "📘 General\n"
    "/start — Main menu\n"
    "/help — Help menu\n"
    "/profile — Your stats\n"
    "/leaderboard — Top players\n\n"

    "⛏ Mining\n"
    "/mine — Mine ores\n"
    "/sell — Sell ores\n"
    "/equip <tool> — Equip tool\n"
    "/repair — Repair tool\n\n"

    "💰 Economy\n"
    "/work — Earn bronze\n"
    "/shop — Buy items\n"
    "/buy <item> — Purchase\n\n"

    "🎲 Games\n"
    "/flip — Coin flip\n"
    "/roll — Dice roll\n"
    "/fight — Fight\n"
    "/rob — Rob user\n"
    "/guess — Guess game\n"
)


def init_help(bot: Client):

    @bot.on_message(filters.private & filters.command("help"))
    async def help_dm(_, msg: Message):
        await msg.reply(HELP_TEXT)

    @bot.on_message(~filters.private & filters.command("help"))
    async def help_group(_, msg: Message):
        username = (await msg._client.get_me()).username
        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("📬 Open Help", url=f"https://t.me/{username}?start=help")]]
        )
        await msg.reply("📬 Help is available in DM:", reply_markup=btn)

    print("[loaded] games.help")
