from pyrogram import Client, filters
from pyrogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
import random
import asyncio
from database.mongo import get_user, update_user
from utils.cooldown import check_cooldown, update_cooldown


def init_flip(bot: Client):

    # --------------------------------------
    # /flip (WORKS IN GROUPS + DM)
    # --------------------------------------
    @bot.on_message(filters.command("flip"))
    async def flip_cmd(_, msg: Message):

        user = msg.from_user
        if not user:
            return

        data = get_user(user.id)

        ok, wait, pretty = check_cooldown(data, "flip", 30)
        if not ok:
            return await msg.reply(f"⏳ Wait **{pretty}** before flipping again.")

        buttons = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🙂 Heads", callback_data="flip_heads"),
                    InlineKeyboardButton("⚡ Tails", callback_data="flip_tails"),
                ]
            ]
        )

        await msg.reply("🪙 **Choose Heads or Tails:**", reply_markup=buttons)

    # --------------------------------------
    # CALLBACK — flip result
    # --------------------------------------
    @bot.on_callback_query(filters.regex(r"^flip_"))
    async def flip_result(_, cq: CallbackQuery):

        user = cq.from_user
        if not user:
            return

        choice = cq.data.replace("flip_", "")
        data = get_user(user.id)

        ok, wait, pretty = check_cooldown(data, "flip", 30)
        if not ok:
            return await cq.answer(f"⏳ Wait {pretty}!", show_alert=True)

        await cq.answer()

        # Animation message
        anim_msg = await cq.message.reply("🪙 Flipping the coin...")
        await asyncio.sleep(1.3)

        actual = random.choice(["heads", "tails"])
        bronze = data.get("bronze", 0)

        if choice == actual:
            reward = random.randint(10, 80)
            bronze += reward
            result_text = (
                f"🎉 **You Won!**\n"
                f"🪙 Coin: **{actual.upper()}**\n"
                f"🥉 Reward: **+{reward} Bronze**"
            )
        else:
            loss = random.randint(5, 35)
            bronze = max(0, bronze - loss)
            result_text = (
                f"😢 **You Lost!**\n"
                f"🪙 Coin: **{actual.upper()}**\n"
                f"🥉 Lost: **-{loss} Bronze**"
            )

        new_cd = update_cooldown(data, "flip")
        update_user(user.id, {"bronze": bronze, "cooldowns": new_cd})

        await anim_msg.edit(result_text)
