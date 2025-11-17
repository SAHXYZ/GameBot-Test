# filename: games/fight.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db
from utils.cooldown import check_cooldown, update_cooldown
import random, asyncio

def init_fight(bot: Client):

    @bot.on_message(filters.command("fight"))
    async def fight_game(_, msg: Message):
        # ignore channel posts
        if not msg.from_user:
            return

        # Must reply to target
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            return await msg.reply("Reply to a user to start a fight!")

        attacker = msg.from_user
        target = msg.reply_to_message.from_user

        if attacker.id == target.id:
            return await msg.reply("You cannot fight yourself!")

        attacker_data = db.get_user(attacker.id)
        target_data = db.get_user(target.id)

        # cooldown check
        ok, wait, pretty = check_cooldown(attacker_data, 'fight', 60)
        if not ok:
            return await msg.reply(f"⏳ You must wait {pretty} before fighting again.")

        # require minimal coins
        if attacker_data.get('coins',0) < 50:
            return await msg.reply("You need at least 50 coins to fight.")

        fight_msg = await msg.reply("⚔️ **Fight Started...**")
        await asyncio.sleep(1); await fight_msg.edit("🥊 **Swinging punches...**")
        await asyncio.sleep(1); await fight_msg.edit("🔥 **Final strike...")

        # Simple outcome: weighted by coins (more coins => higher chance)
        a_power = attacker_data.get('coins',0) + random.randint(1,100)
        t_power = target_data.get('coins',0) + random.randint(1,100)

        if a_power >= t_power:
            # attacker wins
            steal = min(70, target_data.get('coins',0))
            attacker_data['coins'] = attacker_data.get('coins',0) + steal
            target_data['coins'] = max(0, target_data.get('coins',0) - steal)
            attacker_data['fight_wins'] = attacker_data.get('fight_wins',0) + 1
            result = (f"🏆 You won the fight!\n"
                      f"🪙 You gained `{steal}` coins from {target.first_name}.")
        else:
            # attacker loses
            penalty = min(25, attacker_data.get('coins',0))
            attacker_data['coins'] = max(0, attacker_data.get('coins',0) - penalty)
            target_data['coins'] = target_data.get('coins',0) + penalty
            target_data['fight_wins'] = target_data.get('fight_wins',0) + 1
            result = (f"😢 You lost the fight.\n"
                      f"➖ -{penalty} coins\n"
                      f"🏅 {target.first_name} gained `{penalty}` coins.")

        # apply cooldown and save
        attacker_data = update_cooldown(attacker_data, 'fight')
        db.update_user(attacker.id, attacker_data)
        db.update_user(target.id, target_data)

        await fight_msg.edit(result)
