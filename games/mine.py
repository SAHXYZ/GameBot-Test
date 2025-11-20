# games/mine.py
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
import random
import time

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
            "tool_durabilities": {"Wooden": 50},
            "last_mine": 0,
        }
    def update_user(user_id, data):
        pass

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

def weighted_choice(options):
    total = sum(max(0, o.get("weight", 0)) for o in options)
    if total <= 0:
        return None
    pick = random.uniform(0, total)
    upto = 0
    for o in options:
        w = max(0, o.get("weight", 0))
        if upto + w >= pick:
            return o
        upto += w
    return None

def ensure_user_structure(user):
    if user is None:
        return None
    user.setdefault("bronze", 0)
    user.setdefault("tools", {"Wooden": 1})
    user.setdefault("equipped", "Wooden")
    user.setdefault("tool_durabilities", {"Wooden": TOOLS["Wooden"]["durability"]})
    inv = user.setdefault("inventory", {})
    inv.setdefault("ores", {})
    inv.setdefault("items", [])
    user.setdefault("last_mine", 0)
    return user

def mine_action(user_id: int):
    user = ensure_user_structure(get_user(user_id))
    now = time.time()
    if now - user.get("last_mine", 0) < MINE_COOLDOWN:
        return {"success": False, "message": "⏳ Please wait before mining again."}

    equipped = user.get("equipped")
    if not equipped or equipped not in TOOLS:
        return {"success": False, "message": "❌ You have no valid tool equipped. Use /equip <tool>."}

    dur_map = user.setdefault("tool_durabilities", {})
    dur_map.setdefault(equipped, TOOLS[equipped]["durability"])
    if dur_map[equipped] <= 0:
        return {"success": False, "message": f"⚠️ Your {equipped} is broken. Repair it with /repair."}

    tool_power = TOOLS[equipped]["power"]
    available_ores = [o for o in ORES if tool_power >= o.get("min_power", 0)]
    chosen = weighted_choice(available_ores)
    if not chosen:
        return {"success": False, "message": "You dug but found nothing."}

    base_amount = 1
    bonus = random.choices([0, 1, 2], weights=[60, 30, 10])[0]
    amount_found = base_amount + bonus + (tool_power // 3)

    inv_ores = user["inventory"].setdefault("ores", {})
    inv_ores[chosen["name"]] = inv_ores.get(chosen["name"], 0) + amount_found

    # Durability loss
    loss = random.randint(1, 4)
    reduce_by = max(1, int(loss - (tool_power // 5)))
    dur_map[equipped] = max(0, dur_map[equipped] - reduce_by)

    user["last_mine"] = now
    update_user(user_id, user)

    msg = f"⛏️ You mined **{amount_found}x {chosen['name']}** using your {equipped}!\n"
    msg += f"🪵 Durability left: {dur_map[equipped]}"
    if dur_map[equipped] <= 0:
        msg += f"\n⚠️ Your {equipped} broke."

    return {"success": True, "message": msg}

# Command handlers
def cmd_mine(_, message: Message):
    if not message.from_user:
        return
    res = mine_action(message.from_user.id)
    message.reply_text(res["message"])

def cmd_sell_menu(_, message: Message):
    if not message.from_user:
        return
    keyboard = []
    row = []
    for ore in ORES:
        row.append(InlineKeyboardButton(ore["name"], callback_data=f"sell_{ore['name']}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    message.reply_text("🛒 Choose an ore to sell (counts are hidden here; use /profile or /stats to view):",
                       reply_markup=InlineKeyboardMarkup(keyboard))

def cb_sell_handler(_, query: CallbackQuery):
    name = query.data.replace("sell_", "")
    user = ensure_user_structure(get_user(query.from_user.id))
    ores = user["inventory"].get("ores", {})
    if name not in ores or ores.get(name, 0) <= 0:
        return query.answer("❌ You don't have this ore.", show_alert=True)
    amount = ores[name]
    ore_info = next((o for o in ORES if o["name"] == name), None)
    if not ore_info:
        return query.answer("❌ Unknown ore.", show_alert=True)
    gained = amount * ore_info["value"]
    user["bronze"] = user.get("bronze", 0) + gained
    # remove ore
    del ores[name]
    update_user(query.from_user.id, user)
    query.message.edit_text(f"🛒 Sold **{amount}x {name}** for **{gained} Bronze 🥉**!")
    query.answer()

def init_mine(bot: Client):
    # Register handlers (both groups and private)
    bot.add_handler(MessageHandler(cmd_mine, filters.command("mine")), group=0)
    bot.add_handler(MessageHandler(cmd_sell_menu, filters.command("sell")), group=0)
    bot.add_handler(CallbackQueryHandler(cb_sell_handler, filters.regex(r"^sell_")), group=0)
    print("[loaded] games.mine")
