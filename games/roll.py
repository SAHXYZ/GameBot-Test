from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongo import get_user, update_user
from utils.cooldown import check_cooldown, update_cooldown
import asyncio


ROLL_COOLDOWN = 20  # seconds
REWARD_PER_POINT = 10  # bronze per dice point


def init_roll(bot: Client):

    # -----------------------------------------
    # /roll command
    # -----------------------------------------
    @bot.on_message(filters.command(["roll", "dice"]) & filters.private)
    async def roll_cmd(_, msg: Message):
        if not msg.from_user:
            return

        user = get_user(msg.from_user.id)

        ok, wait, pretty = check_cooldown(user, "roll", ROLL_COOLDOWN)
        if not ok:
            return await msg.reply(f"⏳ You must wait **{pretty}** before rolling again!")

        anim = await msg.reply("🎲 Rolling your dice...")

        dice_msg = await bot.send_dice(msg.chat.id)

        await asyncio.sleep(3)
        value = dice_msg.dice.value
        reward = value * REWARD_PER_POINT

        bronze = user.get("bronze", 0) + reward

        # update cooldown + bronze
        cds = update_cooldown(user, "roll")
        update_user(msg.from_user.id, {"bronze": bronze, "cooldowns": cds})

        try:
            await anim.edit(
                f"🎲 **You rolled:** `{value}`\n"
                f"🥉 **Reward:** `{reward} Bronze`"
            )
        except:
            pass

    # -----------------------------------------
    # manual dice message (prevent unlimited farming)
    # -----------------------------------------
    @bot.on_message(filters.dice & filters.private)
    async def dice_msg(_, msg: Message):
        if not msg.from_user:
            return

        if msg.from_user.is_bot:
            return  # ignore bot dice

        user = get_user(msg.from_user.id)

        # apply cooldown
        ok, wait, pretty = check_cooldown(user, "roll", ROLL_COOLDOWN)
        if not ok:
            return await msg.reply(f"⏳ Wait **{pretty}** before rolling again!")

        value = msg.dice.value
        reward = value * REWARD_PER_POINT

        bronze = user.get("bronze", 0) + reward

        cds = update_cooldown(user, "roll")
        update_user(msg.from_user.id, {"bronze": bronze, "cooldowns": cds})

        await msg.reply(
            f"🎲 **Dice rolled:** `{value}`\n"
            f"🥉 **Reward:** `{reward} Bronze`"
        )
