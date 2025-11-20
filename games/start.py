# File: GameBot/GameBot/games/start.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import traceback
from database.mongo import get_user, create_user_if_not_exists

# ==========================================================
# 📌 START TEXT (Home Page)
# ==========================================================
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

# ==========================================================
# 📌 Main Menu Buttons (ONLY 2 BUTTONS — YOUR REQUIREMENT)
# ==========================================================
def get_start_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profile", callback_data="open_profile")],
        [InlineKeyboardButton("❓ Commands", callback_data="help_menu")],
    ])

# ==========================================================
# 📌 Help Menu
# ==========================================================
def get_help_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Help Page", callback_data="help_show")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_home")]
    ])

# ==========================================================
# 📌 Safe async message editor
# ==========================================================
async def safe_edit(message, text, markup=None):
    try:
        if markup:
            return await message.edit_text(text, reply_markup=markup)
        return await message.edit_text(text)
    except:
        return  # silent fail

# ==========================================================
# 📌 Start Handler
# ==========================================================
def init_start(bot: Client):

    @bot.on_message(filters.command("start"))
    async def start_cmd(_, msg: Message):
        try:
            # Ensure user exists
            create_user_if_not_exists(msg.from_user.id, msg.from_user.first_name)

            await msg.reply(
                START_TEXT.format(name=msg.from_user.first_name),
                reply_markup=get_start_menu()
            )

        except Exception:
            traceback.print_exc()
            try:
                await msg.reply("⚠️ Error while starting the bot.")
            except:
                pass

    # ======================================================
    # 📌 HELP MENU callback
    # ======================================================
    @bot.on_callback_query(filters.regex("^help_menu$"))
    async def cb_help(_, q):
        try:
            await safe_edit(q.message, "❓ **Help Menu**", get_help_menu())
            await q.answer()
        except Exception:
            traceback.print_exc()

    # ======================================================
    # 📌 BACK TO HOME
    # ======================================================
    @bot.on_callback_query(filters.regex("^back_to_home$"))
    async def back_home(_, q):
        try:
            await safe_edit(
                q.message,
                START_TEXT.format(name=q.from_user.first_name),
                get_start_menu()
            )
            await q.answer()
        except Exception:
            traceback.print_exc()

    # ======================================================
    # 📌 HELP SHOW PAGE
    # ======================================================
    @bot.on_callback_query(filters.regex("^help_show$"))
    async def help_show(_, q):
        try:
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="help_menu")]
            ])
            await safe_edit(q.message, "ℹ️ Use /help to see all available commands.", kb)
            await q.answer()
        except Exception:
            traceback.print_exc()

    print("[loaded] games.start")
