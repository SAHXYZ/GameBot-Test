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
