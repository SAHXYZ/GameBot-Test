from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import random
import time

# --------------------
# DATABASE
# --------------------
try:
    from database.mongo import get_user, update_user
except Exception:
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

# --------------------
# TOOLS
# --------------------
TOOLS = {
    "Wooden": {"power": 1, "durability": 50, "price": 50},
    "Stone": {"power": 2, "durability": 100, "price": 150},
    "Iron": {"power": 3, "durability": 150, "price": 400},
    "Gold": {"power": 4, "durability": 200, "price": 1200},
    "Platinum": {"power": 5, "durability": 275, "price": 3000},
    "Diamond": {"power": 7, "durability": 350, "price": 8000},
    "Emerald": {"power": 9, "durability": 450, "price": 20000},
}

# --------------------
# ORES
# --------------------
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

# --------------------
# HELPERS
# --------------------
def weighted_choice(opts):
    total = sum(o["weight"] for o in opts)
    pick = random.uniform(0, total)
    cur = 0
    for o in opts:
        if cur + o["weight"] >= pick:
            return o
        cur += o["weight"]
    return opts[-1]


def ensure_user(u):
    u.setdefault("bronze", 0)
    u.setdefault("tools", {"Wooden": 1})
    u.setdefault("equipped", "Wooden")
    u.setdefault("tool_durabilities", {"Wooden": 50})
    inv = u.setdefault("inventory", {})
    inv.setdefault("ores", {})
    inv.setdefault("items", [])
    u.setdefault("last_mine", 0)
    return u


# --------------------
# MINE ACTION
# --------------------
def mine_action(uid):
    user = ensure_user(get_user(uid))
    now = time.time()

    if now - user["last_mine"] < MINE_COOLDOWN:
        return {"success": False, "message": "⏳ Please wait before mining again."}

    eq = user.get("equipped")
    if not eq or eq not in TOOLS:
        return {"success": False, "message": "❌ You have no valid tool equipped."}

    dur = user["tool_durabilities"].setdefault(eq, TOOLS[eq]["durability"])
    if dur <= 0:
        return {"success": False, "message": f"⚠️ Your {eq} is broken. Repair it."}

    usable = [o for o in ORES if TOOLS[eq]["power"] >= o["min_power"]]
    chosen = weighted_choice(usable)

    amount = 1 + random.choice([0, 1, 2]) + (TOOLS[eq]["power"] // 3)

    ores = user["inventory"]["ores"]
    ores[chosen["name"]] = ores.get(chosen["name"], 0) + amount

    user["tool_durabilities"][eq] = max(0, dur - random.randint(1, 4))
    user["last_mine"] = now

    update_user(uid, user)

    return {
        "success": True,
        "message": f"⛏️ You mined **{amount}x {chosen['name']}** using your {eq}!\n🪵 Durability: {user['tool_durabilities'][eq]}"
    }


# --------------------
# COMMAND HANDLERS
# --------------------
def _mine(client, message: Message):
    res = mine_action(message.from_user.id)
    message.reply_text(res["message"])


def _sell_menu(client, message: Message):
    keyboard, row = [], []
    for ore in ORES:
        row.append(InlineKeyboardButton(ore["name"], callback_data=f"sell_{ore['name']}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    message.reply_text("🛒 **Choose an ore to sell:**", reply_markup=InlineKeyboardMarkup(keyboard))


def _sell_handler(client, query: CallbackQuery):
    name = query.data.replace("sell_", "")
    user = ensure_user(get_user(query.from_user.id))
    ores = user["inventory"]["ores"]

    if name not in ores or ores[name] <= 0:
        return query.answer("❌ You don't have this ore.", show_alert=True)

    amount = ores[name]
    price = next(o for o in ORES if o["name"] == name)["value"]
    gained = amount * price

    user["bronze"] += gained
    del ores[name]
    update_user(query.from_user.id, user)

    query.message.edit_text(f"🛒 Sold **{amount}x {name}** for **{gained} Bronze 🥉**!")
    query.answer()


# --------------------
# INIT HANDLERS
# --------------------
def init_mine(bot: Client):
    bot.add_handler(MessageHandler(filters.command("mine"), _mine))
    bot.add_handler(MessageHandler(filters.command("sell"), _sell_menu))
    bot.add_handler(CallbackQueryHandler(_sell_handler))
    print("[loaded] games.mine")
