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

MINE_COOLDOWN = 5

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

def mine_action(uid):
    user = ensure_user(get_user(uid))
    now = time.time()

    if now - user["last_mine"] < MINE_COOLDOWN:
        return {"success": False, "message": "⏳ Please wait before mining again."}

    eq = user["equipped"]
    if eq not in TOOLS:
        return {"success": False, "message": "❌ No tool equipped."}

    dur = user["tool_durabilities"].setdefault(eq, TOOLS[eq]["durability"])
    if dur <= 0:
        return {"success": False, "message": f"⚠️ Your {eq} is broken. Repair it first."}

    usable = [o for o in ORES if TOOLS[eq]["power"] >= o["min_power"]]
    chosen = weighted_choice(usable)

    amount = 1 + random.choice([0, 1, 2]) + (TOOLS[eq]["power"] // 3)

    user["inventory"]["ores"][chosen["name"]] = \
        user["inventory"]["ores"].get(chosen["name"], 0) + amount

    user["tool_durabilities"][eq] = max(0, dur - random.randint(1, 4))
    user["last_mine"] = now

    update_user(uid, user)

    return {
        "success": True,
        "message": f"⛏️ You mined **{amount}× {chosen['name']}**!\n🪵 Durability: {user['tool_durabilities'][eq]}"
    }

def init_mine(bot: Client):

    @bot.on_message(filters.command("mine"))
    async def mine_cmd(_, msg: Message):
        res = mine_action(msg.from_user.id)
        await msg.reply(res["message"])

    @bot.on_message(filters.command("sell"))
    async def sell_cmd(_, msg: Message):
        kb = []
        row = []
        for o in ORES:
            row.append(InlineKeyboardButton(o["name"], callback_data=f"sell_{o['name']}"))
            if len(row) == 2:
                kb.append(row)
                row = []
        if row:
            kb.append(row)

        await msg.reply("🛒 Select ore to sell:", reply_markup=InlineKeyboardMarkup(kb))

    @bot.on_callback_query()
    async def sell_callback(_, cq: CallbackQuery):
        if not cq.data.startswith("sell_"):
            return

        ore = cq.data.replace("sell_", "")
        user = ensure_user(get_user(cq.from_user.id))

        if ore not in user["inventory"]["ores"]:
            return await cq.answer("❌ You don't have this ore.", show_alert=True)

        amount = user["inventory"]["ores"][ore]
        price = next(o["value"] for o in ORES if o["name"] == ore)
        gained = amount * price

        user["bronze"] += gained
        del user["inventory"]["ores"][ore]

        update_user(cq.from_user.id, user)

        await cq.message.edit(f"🛒 Sold **{amount}× {ore}** for **{gained} Bronze 🥉**!")
        await cq.answer()
