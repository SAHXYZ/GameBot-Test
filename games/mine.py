# games/mine.py
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

MINE_COOLDOWN = 5  # seconds


def weighted_choice(options):
    total = sum(max(0, o.get("weight", 0)) for o in options)
    pick = random.uniform(0, total)
    upto = 0
    for o in options:
        w = max(0, o.get("weight", 0))
        if upto + w >= pick:
            return o
        upto += w
    return options[-1] if options else None


def ensure_user_structure(user: dict):
    if user is None:
        return None
    user.setdefault("bronze", 0)
    user.setdefault("tools", {"Wooden": 1})
    user.setdefault("equipped", "Wooden")
    user.setdefault("tool_durabilities", {"Wooden": TOOLS["Wooden"]["durability"]})
    user.setdefault("inventory", {"ores": {}, "items": []})
    user.setdefault("last_mine", 0)
    return user


def do_mine_action(user_id: int):
    user = ensure_user_structure(get_user(user_id))
    now = time.time()

    if now - user.get("last_mine", 0) < MINE_COOLDOWN:
        wait = int(MINE_COOLDOWN - (now - user.get("last_mine", 0)))
        return {"success": False, "message": f"⏳ Wait {wait}s before mining again."}

    equipped = user.get("equipped")
    if not equipped or equipped not in TOOLS:
        return {"success": False, "message": "❌ No valid tool equipped. Use /equip <ToolName> or buy from /shop."}

    # ensure durability exists
    dur_map = user.setdefault("tool_durabilities", {})
    dur_map.setdefault(equipped, TOOLS[equipped]["durability"])
    remaining = dur_map[equipped]
    if remaining <= 0:
        return {"success": False, "message": f"⚠️ Your {equipped} is broken. Repair or equip another tool."}

    power = TOOLS[equipped]["power"]
    available = [o for o in ORES if power >= o.get("min_power", 0)]
    if not available:
        return {"success": False, "message": "This tool cannot mine anything."}

    chosen = weighted_choice(available)
    if not chosen:
        return {"success": False, "message": "You dug but found nothing."}

    amount_found = 1 + random.choices([0, 1, 2], weights=[60, 30, 10])[0] + (power // 3)

    # update inventory (ores)
    inv = user.setdefault("inventory", {})
    ores = inv.setdefault("ores", {})
    ores[chosen["name"]] = ores.get(chosen["name"], 0) + amount_found

    # durability loss (stronger tools wear a bit less)
    loss = random.randint(1, 4)
    reduce_by = max(1, int(loss - (power // 5)))
    dur_map[equipped] = max(0, dur_map[equipped] - reduce_by)

    user["last_mine"] = now
    update_user(user_id, user)

    msg = f"⛏️ You mined {amount_found} x {chosen['name']} with your {equipped}!\n"
    msg += f"🪵 Durability left: {dur_map[equipped]}"

    if dur_map[equipped] <= 0:
        msg += f"\n⚠️ Your {equipped} broke."

    return {"success": True, "message": msg}


def build_sell_keyboard():
    kb = []
    row = []
    for ore in ORES:
        name = ore["name"]
        row.append(InlineKeyboardButton(name, callback_data=f"sell_{name}"))
        if len(row) == 2:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    return InlineKeyboardMarkup(kb)


# init function used by main.py loader; register handlers with decorators
def init_mine(bot: Client):

    @bot.on_message(filters.command("mine"))
    async def cmd_mine(_, msg: Message):
        if not msg.from_user:
            return
        res = do_mine_action(msg.from_user.id)
        await msg.reply(res["message"])

    @bot.on_message(filters.command("sell"))
    async def cmd_sell(_, msg: Message):
        await msg.reply("🛒 Choose ore to sell:", reply_markup=build_sell_keyboard())

    @bot.on_callback_query(filters.regex(r"^sell_"))
    async def cb_sell(_, cq: CallbackQuery):
        ore_name = cq.data.replace("sell_", "")
        user = ensure_user_structure(get_user(cq.from_user.id))
        ores = user.get("inventory", {}).get("ores", {})

        if ore_name not in ores or ores[ore_name] <= 0:
            return await cq.answer("❌ You don't have this ore.", show_alert=True)

        amount = ores[ore_name]
        ore_info = next((o for o in ORES if o["name"] == ore_name), None)
        if ore_info is None:
            return await cq.answer("❌ Invalid ore.", show_alert=True)

        bronze_gain = amount * ore_info["value"]
        user["bronze"] = user.get("bronze", 0) + bronze_gain
        # remove the sold ores
        del user["inventory"]["ores"][ore_name]
        update_user(cq.from_user.id, user)

        await cq.message.edit_text(f"🛒 Sold {amount}x {ore_name} for {bronze_gain} Bronze 🥉")
        await cq.answer()

    print("[loaded] games.mine")
