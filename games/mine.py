# mine.py — Final Version (Fully Integrated)
# - Bronze-only economy
# - Ores stored in inventory["ores"]
# - Shop items stored in inventory["items"]
# - /sell with inline buttons (H2 behavior)
# - No ore counts shown in /sell
# - Compatible with your DB + main.py loader

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import random
import time
from typing import Dict, Any

# -----------------------------
# DATABASE IMPORT
# -----------------------------
try:
    from database.mongo import get_user, update_user
except Exception:
    # fallback for testing
    def get_user(user_id):
        return {
            "_id": str(user_id),
            "bronze": 0,
            "tools": {"Wooden": 1},
            "equipped": "Wooden",
            "inventory": {"ores": {}, "items": []},
            "tool_durabilities": {},
            "last_mine": 0,
        }

    def update_user(user_id, data):
        pass

# -----------------------------
# TOOL + ORE CONFIG
# -----------------------------
TOOLS = {
    "Wooden": {"power": 1, "durability": 50, "tier": "Common", "price": 50},
    "Stone": {"power": 2, "durability": 100, "tier": "Common", "price": 150},
    "Iron": {"power": 3, "durability": 150, "tier": "Uncommon", "price": 400},
    "Gold": {"power": 4, "durability": 200, "tier": "Rare", "price": 1200},
    "Platinum": {"power": 5, "durability": 275, "tier": "Rare", "price": 3000},
    "Diamond": {"power": 7, "durability": 350, "tier": "Epic", "price": 8000},
    "Emerald": {"power": 9, "durability": 450, "tier": "Legendary", "price": 20000},
}

# Ore values = bronze gained per unit when sold
ORES = [
    {"name": "Stone", "min_power": 0, "weight": 50, "value": 1},
    {"name": "Coal", "min_power": 1, "weight": 40, "value": 2},
    {"name": "Iron", "min_power": 2, "weight": 30, "value": 5},
    {"name": "Gold", "min_power": 3, "weight": 15, "value": 25},
    {"name": "Ruby", "min_power": 4, "weight": 8, "value": 60},
    {"name": "Sapphire", "min_power": 5, "weight": 6, "value": 90},
    {"name": "Emerald", "min_power": 6, "weight": 3, "value": 250},
    {"name": "Diamond", "min_power": 7, "weight": 2, "value": 500},
    {"name": "Mythic Crystal", "min_power": 8, "weight": 1, "value": 1500},
]

MINE_COOLDOWN = 5

# -----------------------------
# HELPERS
# -----------------------------

def weighted_choice(options):
    t = sum(o["weight"] for o in options)
    pick = random.uniform(0, t)
    cur = 0
    for o in options:
        if cur + o["weight"] >= pick:
            return o
        cur += o["weight"]
    return options[-1]


def ensure_user(user):
    if user is None:
        return None
    user.setdefault("bronze", 0)
    user.setdefault("tools", {})
    user.setdefault("equipped", None)
    user.setdefault("tool_durabilities", {})
    inv = user.setdefault("inventory", {})
    inv.setdefault("ores", {})
    inv.setdefault("items", [])
    user.setdefault("last_mine", 0)
    return user

# -----------------------------
# MINE ACTION
# -----------------------------

def mine_action(user_id):
    user = ensure_user(get_user(user_id))
    now = time.time()

    if now - user.get("last_mine", 0) < MINE_COOLDOWN:
        return {"success": False, "message": "⏳ Please wait before mining again."}

    equipped = user.get("equipped")
    if not equipped or equipped not in TOOLS:
        return {"success": False, "message": "❌ No valid tool equipped. Use /equip."}

    dur = user["tool_durabilities"].setdefault(equipped, TOOLS[equipped]["durability"])
    if dur <= 0:
        return {"success": False, "message": f"⚠️ Your {equipped} is broken. Repair it."}

    tool_power = TOOLS[equipped]["power"]
    available = [o for o in ORES if tool_power >= o["min_power"]]
    chosen = weighted_choice(available)

    amount = 1 + random.choice([0, 1, 2]) + (tool_power // 3)

    # Update inventory
    ores = user["inventory"]["ores"]
    ores[chosen["name"]] = ores.get(chosen["name"], 0) + amount

    # Durability loss
    loss = random.randint(1, 4)
    user["tool_durabilities"][equipped] = max(0, dur - loss)

    user["last_mine"] = now
    update_user(user_id, user)

    msg = f"⛏️ You mined **{amount}x {chosen['name']}** using your {equipped}!\n"
    msg += f"🪵 Durability left: {user['tool_durabilities'][equipped]}"

    return {"success": True, "message": msg}

# -----------------------------
# /mine
# -----------------------------
@Client.on_message(filters.command("mine") & filters.private)
def _mine(c: Client, m: Message):
    res = mine_action(m.from_user.id)
    m.reply_text(res["message"])

# -----------------------------
# /sell — opens inline keyboard
# -----------------------------
@Client.on_message(filters.command("sell") & filters.private)
def _sell_menu(c: Client, m: Message):
    user = ensure_user(get_user(m.from_user.id))

    keyboard = []
    row = []
    for ore in ORES:
        name = ore["name"]
        row.append(InlineKeyboardButton(name, callback_data=f"sell_{name}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    m.reply_text(
        "🛒 **Choose an ore to sell:**",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# -----------------------------
# SELL CALLBACK (H2 BEHAVIOR)
# -----------------------------
@Client.on_callback_query(filters.regex(r"^sell_"))
def _sell_handler(c: Client, q: CallbackQuery):
    ore_name = q.data.replace("sell_", "")
    user = ensure_user(get_user(q.from_user.id))
    ores = user["inventory"]["ores"]

    # User doesn't have ore → H2 behavior
    if ore_name not in ores or ores[ore_name] <= 0:
        return q.answer("❌ You don't have this ore.", show_alert=True)

    amount = ores[ore_name]
    ore_info = next(o for o in ORES if o["name"] == ore_name)
    bronze_gain = amount * ore_info["value"]

    # Update
    user["bronze"] += bronze_gain
    del ores[ore_name]
    update_user(q.from_user.id, user)

    q.message.edit_text(
        f"🛒 Sold **{amount}x {ore_name}** for **{bronze_gain} Bronze 🥉**!"
    )
    q.answer()

# -----------------------------
# INIT FUNCTION FOR main.py
# -----------------------------
def init_mine(bot: Client):
    print("[loaded] games.mine")

# -----------------------------
# END
# -----------------------------
