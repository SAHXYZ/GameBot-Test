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
# 📌 Main Menu Buttons
# ==========================================================
def get_start_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("👤 Profile", callback_data="open_profile")],
        [
            InlineKeyboardButton("🎮 Games", callback_data="games_menu"),
            InlineKeyboardButton("🛒 Shop", callback_data="shop_menu")
        ],
        [
            InlineKeyboardButton("⛏ Mine", callback_data="mine_menu"),
            InlineKeyboardButton("📊 Top Players", callback_data="top_menu")
        ],
        [InlineKeyboardButton("❓ Help", callback_data="help_menu")],
    ])

# ==========================================================
# 📌 (Optional) Submenus – they can be expanded later
# ==========================================================

def get_games_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎲 Flip", callback_data="game_flip")],
        [InlineKeyboardButton("🎯 Roll", callback_data="game_roll")],
        [InlineKeyboardButton("⚔ Fight", callback_data="game_fight")],
        [InlineKeyboardButton("🔤 Guess", callback_data="game_guess")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_home")],
    ])

def get_help_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📜 Help Page", callback_data="help_show")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_home")],
    ])

# ==========================================================
# 📌 safe_edit function
# ==========================================================
def safe_edit(message, text, markup=None):
    try:
        if markup:
            return message.edit_text(text, reply_markup=markup)
        return message.edit_text(text)
    except:
        return  # fail silently to avoid callback crashes

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
    # 📌 Callback: Menu Navigation
    # ======================================================
    @bot.on_callback_query(filters.regex("^games_menu$"))
    async def games_menu(_, q):
        try:
            safe_edit(q.message, "🎮 **Game Menu**", get_games_menu())
            await q.answer()
        except Exception:
            traceback.print_exc()

    @bot.on_callback_query(filters.regex("^help_menu$"))
    async def help_menu(_, q):
        try:
            safe_edit(q.message, "❓ **Help Menu**", get_help_menu())
            await q.answer()
        except Exception:
            traceback.print_exc()

    @bot.on_callback_query(filters.regex("^mine_menu$"))
    async def mine_menu(_, q):
        try:
            text = (
                "⛏ **Mining Menu**\n\n"
                "Use /mine to gather ores.\n"
                "Sell your ores by clicking buttons after mining.\n"
            )
            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_home")]
            ])
            safe_edit(q.message, text, kb)
            await q.answer()
        except Exception:
            traceback.print_exc()

    @bot.on_callback_query(filters.regex("^top_menu$"))
    async def top_menu(_, q):
        try:
            safe_edit(q.message, "📊 *Top Players coming soon...*", InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back", callback_data="back_to_home")]
            ]))
            await q.answer()
        except Exception:
            traceback.print_exc()

    @bot.on_callback_query(filters.regex("^help_show$"))
    async def help_show(_, q):
        try:
            safe_edit(
                q.message,
                "ℹ️ Use /help to see all available commands.",
                InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="help_menu")]])
            )
            await q.answer()
        except Exception:
            traceback.print_exc()

    print("[loaded] games.start")
