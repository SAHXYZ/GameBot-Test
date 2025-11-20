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

# (NOTE: keep your ORES and other logic as-is — truncated here in the snippet for brevity)
# Make sure to keep the rest of the original logic, but I include some robustness below.

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

        # Example mining logic (use your real logic here)
        # Simple cooldown example:
        now = int(time.time())
        if user.get("last_mine", 0) + 5 > now:
            await msg.reply("⏳ You're mining too fast. Wait a few seconds.")
            return
        user["last_mine"] = now

        # choose ore based on tool power or random
        ore = "Stone"  # replace with your selection logic
        gained_amount = random.randint(1, 3)
        user["inventory"]["ores"].setdefault(ore, 0)
        user["inventory"]["ores"][ore] += gained_amount

        update_user(msg.from_user.id, user)
        await msg.reply(f"⛏️ You mined {gained_amount}× {ore}!")

    # Add callback handlers (ensure we imported CallbackQuery above)
    @bot.on_callback_query(filters.regex("^sell_ore:"))
    async def cb_sell_ore(_, cq: CallbackQuery):
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

        # price lookup safety (your ORES list should contain dicts with 'name' and 'value')
        price = 1
        # try to find price from ORES if available
        try:
            price = next((o["value"] for o in ORES if o["name"] == ore), 1)
        except Exception:
            price = 1

        gained = amount * price
        user["bronze"] = user.get("bronze", 0) + gained
        # remove the ore entry safely
        user.setdefault("inventory", {}).setdefault("ores", {})
        user["inventory"]["ores"].pop(ore, None)
        update_user(cq.from_user.id, user)

        await cq.message.edit_text(f"🛒 Sold **{amount}× {ore}** for **{gained} Bronze 🥉**!")
        await cq.answer()
