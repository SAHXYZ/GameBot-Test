# File: GameBot/games/help.py
from pyrogram import Client, filters
from pyrogram.types import Message
import traceback


def init_help(bot: Client):

    @bot.on_message(filters.command(["help", "commands"]))
    async def help_cmd(_, msg: Message):
        try:
            text = (
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

            await msg.reply_text(
                text,
                parse_mode="html",   # ← IMPORTANT FIX
                disable_web_page_preview=True
            )

        except Exception:
            traceback.print_exc()
            try:
                await msg.reply_text("⚠️ Failed to load help menu.")
            except:
                pass
