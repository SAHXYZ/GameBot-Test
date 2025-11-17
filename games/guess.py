# filename: games/guess.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db
import random

active_games = {}  # user_id -> {word, hint}

WORD_LIST = [
    'apple','brain','chair','dream','eagle','flame','globe','heart','island','joker',
    'knife','lemon','magic','night','ocean','piano','queen','river','stone','train',
    'urban','vivid','whale','xenon','yacht','zebra'
]

def generate_hint(word):
    # show first and last letters and underscores for rest
    if len(word) <= 2:
        return word
    return word[0] + ''.join('_' for _ in word[1:-1]) + word[-1]

def init_guess(bot: Client):

    @bot.on_message(filters.command("guess"))
    async def start_guess(_, msg: Message):
        if not msg.from_user:
            return
        user_id = str(msg.from_user.id)
        if user_id in active_games:
            return await msg.reply("You already have an active guess game. Use /stop to end it.")

        word = random.choice(WORD_LIST)
        hint = generate_hint(word)
        active_games[user_id] = {"word": word, "hint": hint}
        await msg.reply(f"🔤 Word Guess Started! Hint: `{hint}`\nReply with /answer <word> to guess.")

    @bot.on_message(filters.command("answer"))
    async def process_guess(_, msg: Message):
        if not msg.from_user:
            return
        args = msg.text.split(maxsplit=1)
        if len(args) < 2:
            return await msg.reply("Usage: /answer <word>")
        user_id = str(msg.from_user.id)
        if user_id not in active_games:
            return await msg.reply("You have no active guess game. Start with /guess.")

        guess = args[1].strip().lower()
        correct = active_games[user_id]["word"].lower()
        if guess == correct:
            reward = random.randint(50,150)
            user = db.get_user(msg.from_user.id)
            user['coins'] = user.get('coins',0) + reward
            db.update_user(msg.from_user.id, user)
            del active_games[user_id]
            await msg.reply(f"🎉 Correct! You earned `{reward}` coins.")
        else:
            await msg.reply("❌ Wrong guess. Try again or /stop to end the game.")

    @bot.on_message(filters.command("stop"))
    async def stop_guess(_, msg: Message):
        if not msg.from_user:
            return
        user_id = str(msg.from_user.id)
        if user_id in active_games:
            del active_games[user_id]
            return await msg.reply("Stopped your guess game.")
        await msg.reply("You have no active guess game.")
