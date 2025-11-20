from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode
import traceback


def init_help(bot: Client):

    @bot.on_message(filters.command(["help", "commands"]))
    async def help_cmd(_, msg: Message):
        try:

            # ---------- FULL HELP (Private Chat) ----------
            full_help = (
                "⚙️ ● <b><i>HELP CENTER</i></b>\n\n"
                "⟡ <b><i>Profile</i></b>\n"
                "• /profile — View Your Profile\n\n"
                "⟡ <b><i>Games</i></b>\n"
                "• /flip — Coin Flip Duel\n"
                "• /roll — Dice Roll\n"
                "• /fight — Fight Another Player\n"
                "• /rob — Rob a Player (Risk + Reward)\n"
                "• /guess — Guess the Hidden Word\n\n"
                "⟡ <b><i>Mining</i></b>\n"
                "• /mine — Mine Ores\n"
                "• /sell — Sell Your Mined Ores\n\n"
                "⟡ <b><i>Shop</i></b>\n"
                "• /shop — View Shop Items\n"
                "• /buy — Buy Items/Tools\n\n"
                "⟡ <b><i>Other</i></b>\n"
                "• /leaderboard — Top Players\n"
                "• /work — Earn Bronze Coins\n\n"
                "⟡ <i>Tip: You Should Use These Commands In Bot's Personal Chat "
                "For Better Performance.</i> ⚡️"
            )

            # ---------- SHORT HELP FOR GROUP ----------
            group_help = (
                "⚙️ ● <b>HELP CENTER</b>\n\n"
                "⟡ <i>Tip: You Should Use These Commands In Bot's Personal Chat "
                "For Better Performance!</i> ⚡️"
            )

            # Deep-link to open PM help
            deep_link = f"https://t.me/{(await bot.get_me()).username}?start=help"

            # Keyboard for groups
            group_kb = InlineKeyboardMarkup(
                [[InlineKeyboardButton("📘 Help & Commands", url=deep_link)]]
            )

            # Detect chat type
            if msg.chat.type in ("supergroup", "group"):
                # Send short help in group
                await msg.reply_text(
                    group_help,
                    parse_mode=ParseMode.HTML,
                    reply_markup=group_kb
                )
            else:
                # Send full help in PM
                await msg.reply_text(
                    full_help,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True
                )

        except Exception:
            traceback.print_exc()
            await msg.reply_text("⚠️ Failed to load help menu.")
