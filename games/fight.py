from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongo import get_user, update_user
from utils.cooldown import check_cooldown, update_cooldown
import random, asyncio

def init_fight(bot: Client):

    @bot.on_message(filters.command("fight"))
    async def fight_game(_, msg: Message):

        if not msg.from_user:
            return

        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            return await msg.reply("Reply to a user to start a fight!")

        attacker = msg.from_user
        defender = msg.reply_to_message.from_user

        if attacker.id == defender.id:
            return await msg.reply("You cannot fight yourself!")

        a_data = get_user(attacker.id)
        d_data = get_user(defender.id)

        ok, wait, pretty = check_cooldown(a_data, "fight", 60)
        if not ok:
            return await msg.reply(f"⏳ You must wait **{pretty}** before fighting again.")

        a_bronze = a_data.get("bronze", 0)
        d_bronze = d_data.get("bronze", 0)

        fight_msg = await msg.reply("⚔️ **Fight Started...**")
        await asyncio.sleep(1)
        await fight_msg.edit("🥊 **Throwing punches...**")
        await asyncio.sleep(1)
        await fight_msg.edit("🔥 **Final Strike Incoming...**")
        await asyncio.sleep(1)

        a_power = a_bronze + random.randint(1, 120)
        d_power = d_bronze + random.randint(1, 120)

        if a_power >= d_power:
            steal = random.randint(10, 100)
            steal = min(steal, d_bronze)

            new_a_bronze = a_bronze + steal
            new_d_bronze = max(0, d_bronze - steal)
            a_wins = a_data.get("fight_wins", 0) + 1

            result = (
                f"🏆 **You Won the Fight!**\n"
                f"🥉 You stole **{steal} Bronze** from **{defender.first_name}**!"
            )

            update_user(attacker.id, {"bronze": new_a_bronze, "fight_wins": a_wins})
            update_user(defender.id, {"bronze": new_d_bronze})

        else:
            penalty = random.randint(5, 50)
            penalty = min(penalty, a_bronze)

            new_a_bronze = max(0, a_bronze - penalty)
            new_d_bronze = d_bronze + penalty
            d_wins = d_data.get("fight_wins", 0) + 1

            result = (
                f"😢 **You Lost the Fight!**\n"
                f"➖ You lost **{penalty} Bronze**.\n"
                f"🏆 **{defender.first_name}** gained **{penalty} Bronze**!"
            )

            update_user(attacker.id, {"bronze": new_a_bronze})
            update_user(defender.id, {"bronze": new_d_bronze, "fight_wins": d_wins})

        new_cooldowns = update_cooldown(a_data, "fight")
        update_user(attacker.id, {"cooldowns": new_cooldowns})

        await fight_msg.edit(result)
