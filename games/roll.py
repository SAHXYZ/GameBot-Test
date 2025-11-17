# filename: games/roll.py

from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db
import random
import asyncio

def init_roll(bot: Client):

    # /roll or /dice command
    @bot.on_message(filters.command(["roll", "dice"]))
    async def roll_cmd(_, msg: Message):

        if not msg.from_user:
            return

        user = db.get_user(msg.from_user.id)

        # Random dice roll
        value = random.randint(1, 6)
        reward = value * 10

        user["coins"] += reward
        db.update_user(msg.from_user.id, user)

        await msg.reply(
            f"🎲 **You rolled:** `{value}`\n"
            f"💰 **Reward:** {reward} coins"
        )

    # Detect Telegram dice message (when user taps 🎲 button)
    @bot.on_message(filters.dice)
    async def dice_msg(_, msg: Message):

        if not msg.from_user:
            return

        user = db.get_user(msg.from_user.id)
        value = msg.dice.value  # Telegram gives actual dice value
        reward = value * 10

        user["coins"] += reward
        db.update_user(msg.from_user.id, user)

        await msg.reply(
            f"🎲 Dice rolled: `{value}`\n"
            f"💰 Reward: **{reward} coins**"
        )
