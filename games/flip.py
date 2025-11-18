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

        user = db.get_user(msg.from_user.id)

        ok, wait, pretty = check_cooldown(user, "flip", 300)
        if not ok:
            return await msg.reply(f"⏳ You must wait **{pretty}** before flipping again!")

        # Buttons for choosing side
        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🙂 Heads", callback_data="flip_heads"),
                    InlineKeyboardButton("⚡ Tails", callback_data="flip_tails"),
                ]
            ]
        )

        await msg.reply("🎮 **Choose your side:**", reply_markup=buttons)

    # Callback for flip
    @bot.on_callback_query(filters.regex(r"flip_"))
    async def flip_result(_, cq: CallbackQuery):
        choice = cq.data.replace("flip_", "")  # heads / tails
        user = db.get_user(cq.from_user.id)

        ok, wait, pretty = check_cooldown(user, "flip", 30)
        if not ok:
            return await cq.answer(f"⏳ Wait {pretty}!", show_alert=True)

        await cq.answer()

        # Cool animation
        anim_msg = await cq.message.reply("🪙 Flipping coin...")
        await asyncio.sleep(1.2)

        # True 50/50 probability
        actual = random.choice(["heads", "tails"])

        # Bronze reward system (random 1–100 for win)
        reward = random.randint(1, 100)

        # For losing, remove only bronze and not below 0
        penalty = random.randint(1, 40)  # Losing penalty balanced

        bronze = user.get("bronze", 0)

        # Outcome
        if choice == actual:
            user["bronze"] = bronze + reward
            outcome_text = (
                f"🎉 **You Won!**\n"
                f"🪙 Coin was **{actual.upper()}**\n"
                f"🥉 You earned **+{reward} Bronze**!"
            )
        else:
            user["bronze"] = max(0, bronze - penalty)
            outcome_text = (
                f"😢 **You Lost!**\n"
                f"🪙 Coin was **{actual.upper()}**\n"
                f"🥉 You lost **-{penalty} Bronze**."
            )

        # Update cooldown + save DB
        user = update_cooldown(user, "flip")
        db.update_user(cq.from_user.id, user)

        # Edit animation to outcome
        await anim_msg.edit(outcome_text)
