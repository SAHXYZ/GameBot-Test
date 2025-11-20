# File: GameBot/GameBot/games/mine.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random
import time
import traceback
from database.mongo import get_user, update_user

# 🔨 Tools with power & durability
TOOLS = {
    "Wooden": {"power": 1, "durability": 50, "price": 50},
    "Stone": {"power": 2, "durability": 100, "price": 150},
    "Iron": {"power": 3, "durability": 150, "price": 400},
    "Gold": {"power": 4, "durability": 200, "price": 1200},
    "Platinum": {"power": 5, "durability": 275, "price": 3000},
    "Diamond": {"power": 7, "durability": 350, "price": 8000},
    "Emerald": {"power": 9, "durability": 450, "price": 20000},
}

# 💎 Ore table
ORES = [
    {"name": "Coal", "value": 2, "rarity": 60},
    {"name": "Copper", "value": 5, "rarity": 45},
    {"name": "Iron", "value": 12, "rarity": 30},
    {"name": "Gold", "value": 25, "rarity": 15},
    {"name": "Diamond", "value": 100, "rarity": 5},
]

# Weighted ore picking based on rarity
def choose_ore():
    pool = []
    for ore in ORES:
        pool.extend([ore["name"]] * max(1, ore["rarity"]))
    return random.choice(pool) if pool else "Coal"


def init_mine(bot: Client):

    # ⛏️ /mine command
    @bot.on_message(filters.command("mine") & ~filters.edited)
    async def mine_cmd(_, msg: Message):
        try:
            user = get_user(msg.from_user.id)
            if not user:
                await msg.reply("❌ Please use /start first to create your profile.")
                return

            # Ensure structures exist
            user.setdefault("inventory", {})
            user["inventory"].setdefault("ores", {})

            now = int(time.time())
            cooldown = 5  # seconds cooldown
            last = user.get("last_mine", 0)

            # Cooldown logic
            if last + cooldown > now:
                wait = (last + cooldown) - now
                await msg.reply(f"⏳ You're mining too fast! Wait **{wait}s**.")
                return

            user["last_mine"] = now

            ore = choose_ore()
            amount = random.randint(1, 3)

            user["inventory"]["ores"].setdefault(ore, 0)
            user["inventory"]["ores"][ore] += amount

            update_user(msg.from_user.id, user)

            kb = InlineKeyboardMarkup([
                [InlineKeyboardButton(f"Sell {amount}× {ore}", callback_data=f"sell_ore:{ore}")]
            ])

            await msg.reply(f"⛏️ You mined **{amount}× {ore}**!", reply_markup=kb)

        except Exception:
            traceback.print_exc()
            try:
                await msg.reply("⚠️ An error occurred during mining.")
            except:
                pass

    # 💰 Callback: Sell ore
    @bot.on_callback_query(filters.regex(r"^sell_ore:"))
    async def sell_ore(_, cq: CallbackQuery):
        try:
            ore = cq.data.split(":", 1)[1]

            user = get_user(cq.from_user.id)
            if not user:
                await cq.answer("Profile not found.")
                return

            user.setdefault("inventory", {})
            user["inventory"].setdefault("ores", {})
            ores = user["inventory"]["ores"]

            amount = ores.get(ore, 0)
            if amount <= 0:
                await cq.answer("You have no ore to sell!")
                return

            price = next((o["value"] for o in ORES if o["name"] == ore), 1)
            earned = amount * price

            # Add bronze safely
            user["bronze"] = user.get("bronze", 0) + earned

            # Remove ore
            ores.pop(ore, None)

            update_user(cq.from_user.id, user)

            try:
                await cq.message.edit_text(f"🛒 Sold **{amount}× {ore}** for **{earned} Bronze 🥉**!")
            except Exception:
                await cq.answer(f"Sold {amount}× {ore} for {earned} Bronze.")

            await cq.answer()

        except Exception:
            traceback.print_exc()
            try:
                await cq.answer("⚠️ Error selling ore.")
            except:
                pass
