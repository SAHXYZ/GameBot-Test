# filename: games/start.py

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

def init_start(bot: Client):

    @bot.on_message(filters.command("start"))
    async def start_handler(_, msg: Message):

        name = msg.from_user.first_name

        text = (
            f"Hᴇʏ {name}\n\n"
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

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🕹 Commands", callback_data="show_commands"),
                    InlineKeyboardButton("👤 Profile", callback_data="show_profile"),
                ]
            ]
        )

        await msg.reply(text, reply_markup=buttons)

# filename: games/help.py

from pyrogram import Client, filters

def init_help(bot: Client):

    @bot.on_message(filters.command("help"))
    async def help_cmd(_, msg):
        text = (
            "🎮 **GameBot Commands**\n\n"
            "**General Commands**\n"
            "/start - Show menu\n"
            "/help - Show this help menu\n"
            "/profile - Your stats\n"
            "/leaderboard - Top players\n\n"
            "**Game Commands**\n"
            "/flip - Coin flip game\n"
            "/roll - Random dice roll\n"
            "/fight - Fight another user\n"
            "/rob - Rob a user\n"
            "/guess - Word guessing game\n"
            "/work - Earn coins by working\n"
            "/shop - Purchase items\n"
        )

        await msg.reply(text)
