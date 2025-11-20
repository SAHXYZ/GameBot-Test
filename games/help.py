# File: GameBot/GameBot/games/help.py
from pyrogram import Client, filters
from pyrogram.types import Message
import traceback

def init_help(bot: Client):
    """
    Register the /help command.
    Keeps the handler simple, defensive, and safe for both private chats and groups.
    """

    @bot.on_message(filters.command(["help", "commands"]))
    async def help_cmd(_, msg: Message):
        try:
            text = (
                "🎮 **GameBot Help Menu**\n\n"

                "📌 **General Commands**\n"
                "/start - Main menu\n"
                "/help or /commands - This help menu\n"
                "/profile - Show your profile\n"
                "/inv - Show inventory\n"
                "/work - Earn bronze\n"
                "/shop - Buy items\n"
                "/buy <item> - Purchase item\n\n"

                "🎮 **Games**\n"
                "/flip - Coin flip\n"
                "/roll - Dice roll\n"
                "/fight - Fight users\n"
                "/rob - Rob users\n"
                "/guess - Word guessing game\n"
                "/mine - Mine ores (earn resources)\n\n"

                "ℹ️ Tip: Use commands in private chat for a full interactive experience. "
                "Some commands may require you to have a profile (use /start if you haven't)."
            )

            # Reply — use reply_text to keep formatting explicit
            await msg.reply_text(text)
        except Exception as e:
            # Defensive fallback: try to notify user, but don't crash the bot
            try:
                await msg.reply_text("⚠️ An error occurred while showing help.")
            except Exception:
                pass
            # Print traceback to server logs for debugging
            traceback.print_exc()
