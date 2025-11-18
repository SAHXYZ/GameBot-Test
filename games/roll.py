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

        # Send animated dice
        anim = await msg.reply("🎲 Rolling...")
        dice_msg = await msg.reply_dice()  # Telegram animation

        # Wait until animation finishes
        await asyncio.sleep(3)

        # Value from dice
        value = dice_msg.dice.value
        reward = value * 10  # Bronze reward

        # Update bronze only
        user["bronze"] = user.get("bronze", 0) + reward
        db.update_user(msg.from_user.id, user)

        await anim.edit(
            f"🎲 **You rolled:** `{value}`\n"
            f"🥉 **Reward:** `{reward} Bronze`"
        )

    # Detect Telegram dice message (when user taps 🎲 button)
    @bot.on_message(filters.dice)
    async def dice_msg(_, msg: Message):

        if not msg.from_user:
            return

        user = db.get_user(msg.from_user.id)
        value = msg.dice.value
        reward = value * 10

        user["bronze"] = user.get("bronze", 0) + reward
        db.update_user(msg.from_user.id, user)

        await msg.reply(
            f"🎲 Dice rolled: `{value}`\n"
            f"🥉 Reward: `{reward} Bronze`"
        )
