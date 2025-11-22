# File: games/daily.py

from pyrogram import filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import random
import asyncio

from database.mongo import get_user, update_user


BRONZE_REWARD = 100


def random_crate():
    roll = random.random() * 100
    if roll <= 80:
        return ("Bronze Crate", random.randint(80, 140))
    elif roll <= 95:
        return ("Gold Crate", random.randint(300, 500))
    else:
        return ("Diamond Crate", random.randint(1000, 1500))


async def daily_handler(client, msg: Message):
    user_id = msg.from_user.id
    user = await get_user(user_id)

    last_time = user.get("last_daily", None)

    if last_time is not None:
        available_time = last_time + timedelta(hours=24)
        if datetime.now() < available_time:
            remaining = available_time - datetime.now()
            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            return await msg.reply(
                f"⏳ **Daily already claimed!**\n"
                f"Come back in **{hours}h {minutes}m**."
            )

    anim_msg = await msg.reply("🎁 | Opening daily crate...")
    await asyncio.sleep(1)

    await anim_msg.edit("📦 | Crate received...")
    await asyncio.sleep(1)

    await anim_msg.edit("🔄 | Crate is shaking...")
    await asyncio.sleep(1)

    await anim_msg.edit("✨ | Crate is opening...")
    await asyncio.sleep(1)

    crate_name, reward_amount = random_crate()

    await update_user(user_id, {
        "bronze": user.get("bronze", 0) + reward_amount,
        "last_daily": datetime.now()
    })

    await anim_msg.edit(
        f"🎉 **DAILY REWARD CLAIMED!**\n\n"
        f"📦 **{crate_name} Unlocked!**\n"
        f"💰 **+{reward_amount} Bronze** added to your wallet.\n\n"
        f"Come back again after **24 hours**!"
    )


# ---- REQUIRED for loading in main.py ----
def init_daily(bot):
    bot.add_handler(
        filters.command("daily")(daily_handler)
    )
    print(" -> daily module initialized")
