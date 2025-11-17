# filename: games/rob.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db
from utils.cooldown import check_cooldown, update_cooldown
import random, asyncio

def init_rob(bot: Client):

    @bot.on_message(filters.command("rob"))
    async def rob_game(_, msg: Message):
        if not msg.from_user:
            return

        # Must reply to a user to rob
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            return await msg.reply("Reply to a user to rob them!")

        robber = msg.from_user
        victim = msg.reply_to_message.from_user

        if robber.id == victim.id:
            return await msg.reply("You cannot rob yourself.")

        robber_data = db.get_user(robber.id)
        victim_data = db.get_user(victim.id)

        ok, wait, pretty = check_cooldown(robber_data, 'rob', 300)
        if not ok:
            return await msg.reply(f"⏳ You must wait {pretty} before robbing again.")

        # chance to succeed
        success = random.random() < 0.45  # 45% success

        rob_msg = await msg.reply("🕵️ Trying to rob...")

        await asyncio.sleep(1)
        if not success:
            loss = min(30, robber_data.get('coins',0))
            robber_data['coins'] = max(0, robber_data.get('coins',0) - loss)
            victim_data['coins'] = victim_data.get('coins',0) + loss
            robber_data = update_cooldown(robber_data, 'rob')
            db.update_user(robber.id, robber_data)
            db.update_user(victim.id, victim_data)
            return await rob_msg.edit(f"🚨 Robbery failed! You were fined `{loss}` coins.")

        # success: steal a percentage of victim's coins
        available = victim_data.get('coins',0)
        if available <= 0:
            robber_data = update_cooldown(robber_data, 'rob')
            db.update_user(robber.id, robber_data)
            return await rob_msg.edit("😶 Target has no coins to steal.")

        amount = min(available, random.randint(20, min(250, available)))
        victim_data['coins'] = max(0, victim_data.get('coins',0) - amount)
        robber_data['coins'] = robber_data.get('coins',0) + amount

        robber_data = update_cooldown(robber_data, 'rob')
        db.update_user(robber.id, robber_data)
        db.update_user(victim.id, victim_data)

        await rob_msg.edit(f"💰 Robbery successful! You stole `{amount}` coins from {victim.first_name}.")
