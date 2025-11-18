from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from database.mongo import get_user

from utils.coins import total_bronze_value, breakdown_from_bronze

def build_profile_text_for_user(user: dict, mention: str):
    black_gold = int(user.get("black_gold", 0) or 0)
    platinum   = int(user.get("platinum", 0) or 0)
    gold       = int(user.get("gold", 0) or 0)
    silver     = int(user.get("silver", 0) or 0)
    bronze     = int(user.get("bronze", 0) or 0)

    total_bronze = total_bronze_value(user)

    badge_text = " ".join(user.get("badges", [])) if user.get("badges") else "None"
    inv_text = ", ".join(user.get("inventory", [])) if user.get("inventory") else "No items"

    text = (
        f"👤 **Profile of {mention}**\n\n"
        f"🎖 **Black Gold:** `{black_gold}` (purchasable / events only)\n\n"
        f"🏅 **Platinum:** `{platinum}`\n"
        f"🥇 **Gold:** `{gold}`\n"
        f"🥈 **Silver:** `{silver}`\n"
        f"🥉 **Bronze:** `{bronze}`\n\n"
        f"🔢 **Total (bronze-equivalent):** `{total_bronze}`\n\n"
        f"💬 **Messages Sent:** `{user.get('messages', 0)}`\n\n"
        f"🥊 **Fight Wins:** `{user.get('fight_wins', 0)}`\n"
        f"🕵️ **Successful Robberies:** `{user.get('rob_success', 0)}`\n"
        f"🚨 **Failed Robberies:** `{user.get('rob_fail', 0)}`\n\n"
        f"🎖 **Badges:** {badge_text}\n"
        f"🛒 **Inventory:** {inv_text}"
    )
    return text

def get_profile_markup():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⬅️ Back", callback_data="back_to_home")]
        ]
    )

def init_profile(bot: Client):

    @bot.on_message(filters.command("profile"))
    async def profile(_, msg: Message):

        if not msg.from_user:
            return

        user = get_user(msg.from_user.id)
        text = build_profile_text_for_user(user, msg.from_user.mention)
        await msg.reply(text, reply_markup=get_profile_markup())
