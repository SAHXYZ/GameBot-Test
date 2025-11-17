# filename: games/flip.py

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database_main import db
from utils.cooldown import check_cooldown, update_cooldown
import random
import asyncio


def init_flip(bot: Client):

    @bot.on_message(filters.command("flip"))
    async def flip_cmd(_, msg):
        if not msg.from_user:
            return


        if not msg.from_user:


            return


        user = db.get_user(msg.from_user.id)
        ok, wait, pretty = check_cooldown(user, "flip", 30)
        if not ok:
            return await msg.reply(f"⏳ You must wait **{pretty}** before flipping again!")

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🙂 Heads", callback_data="flip_heads"),
                    InlineKeyboardButton("⚡ Tails", callback_data="flip_tails"),
                ]
            ]
        )

        await msg.reply("🎮 **Choose your side:**", reply_markup=buttons)

    @bot.on_callback_query(filters.regex(r"flip_"))
    async def flip_result(_, cq: CallbackQuery):
        choice = cq.data.replace("flip_", "")  # heads / tails
        user = db.get_user(cq.from_user.id)

        ok, wait, pretty = check_cooldown(user, "flip", 30)
        if not ok:
            return await cq.answer(f"⏳ Wait {pretty}!", show_alert=True)

        # Coin animation (Telegram renders 🪙 as a spinning animation)
        anim_msg = await cq.message.reply("🪙")

        await cq.answer()  # closes the loading circle
        await asyncio.sleep(1.2)

        actual = random.choice(["heads", "tails"])

        # Result
        coins = user.get("coins", 0)

        if choice == actual:
            reward = 50
            user["coins"] = coins + reward
            text = (
                f"🎉 **You Won!**\n"
                f"🪙 It was **{actual.upper()}**\n"
                f"➕ +{reward} coins"
            )
        else:
            penalty = 25
            user["coins"] = max(0, coins - penalty)
            text = (
                f"😢 **You Lost!**\n"
                f"🪙 It was **{actual.upper()}**\n"
                f"➖ -{penalty} coins"
            )

        user = update_cooldown(user, "flip")
        db.update_user(cq.from_user.id, user)

        await anim_msg.edit(text)
