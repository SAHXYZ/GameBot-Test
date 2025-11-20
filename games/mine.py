# File: GameBot/GameBot/games/mine.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random, time
from database.mongo import get_user, update_user

TOOLS = {
    "Wooden": {"power": 1, "durability": 50, "price": 50},
    "Stone": {"power": 2, "durability": 100, "price": 150},
    "Iron": {"power": 3, "durability": 150, "price": 400},
    "Gold": {"power": 4, "durability": 200, "price": 1200},
    "Platinum": {"power": 5, "durability": 275, "price": 3000},
    "Diamond": {"power": 7, "durability": 350, "price": 8000},
    "Emerald": {"power": 9, "durability": 450, "price": 20000},
}

ORES = [
    {"name": "Coal", "value": 2, "rarity": 60},
    {"name": "Copper", "value": 5, "rarity": 45},
    {"name": "Iron", "value": 12, "rarity": 30},
    {"name": "Gold", "value": 25, "rarity": 15},
    {"name": "Diamond", "value": 100, "rarity": 5},
]

def choose_ore():
    # choose ore by weighted rarity
    pool = []
    for o in ORES:
        pool.extend([o["name"]] * max(1, int(o.get("rarity", 1))))
    return random.choice(pool) if pool else ORES[0]["name"]

def init_mine(bot: Client):

    @bot.on_message(filters.command("mine"))
    async def cmd_mine(_, msg: Message):
        user = get_user(msg.from_user.id)
        if user is None:
            await msg.reply("❌ Could not find your user profile. Try /start first.")
            return

        # Ensure inventory structure exists
        user.setdefault("inventory", {})
        user["inventory"].setdefault("ores", {})

        now = int(time.time())
        cooldown = 5  # seconds between mines (adjust as needed)
        if user.get("last_mine", 0) + cooldown > now:
            await msg.reply(f"⏳ You're mining too fast. Wait a few seconds.")
            return
        user["last_mine"] = now

        # Determine ore and amount
        ore = choose_ore()
        gained_amount = random.randint(1, 3)

        user["inventory"]["ores"].setdefault(ore, 0)
        user["inventory"]["ores"][ore] += gained_amount

        update_user(msg.from_user.id, user)
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Sell all", callback_data=f"sell_ore:{ore}")]]
        )
        await msg.reply(f"⛏️ You mined {gained_amount}× {ore}!", reply_markup=kb)

    @bot.on_callback_query(filters.regex(r"^sell_ore:"))
    async def cb_sell_ore(_, cq: CallbackQuery):
        try:
            parts = cq.data.split(":", 1)
            if len(parts) != 2:
                await cq.answer("Invalid sell command.")
                return
            ore = parts[1]
            user = get_user(cq.from_user.id)
            if not user:
                await cq.answer("User not found.")
                return

            ores = user.get("inventory", {}).get("ores", {})
            amount = ores.get(ore, 0)
            if amount <= 0:
                await cq.answer("No ore to sell.")
                return

            # price lookup safety
            price = next((o["value"] for o in ORES if o["name"] == ore), 1)
            gained = amount * price

            user["bronze"] = user.get("bronze", 0) + gained
            user.setdefault("inventory", {}).setdefault("ores", {})
            user["inventory"]["ores"].pop(ore, None)
            update_user(cq.from_user.id, user)

            # If message exists, edit; otherwise respond
            try:
                await cq.message.edit_text(f"🛒 Sold **{amount}× {ore}** for **{gained} Bronze 🥉**!")
            except Exception:
                await cq.answer(f"Sold {amount}× {ore} for {gained} Bronze.")
            await cq.answer()
        except Exception as e:
            # safe fallback
            try:
                await cq.answer("Error processing sell request.")
            except:
                pass
