# filename: games/shop.py

from pyrogram import Client, filters
from pyrogram.types import (
    Message, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    CallbackQuery
)
from database.mongo import get_user, update_user


# ---------------------------------------
# SHOP DATA
# ---------------------------------------
ITEMS = [
    ("Lucky Charm 🍀", 200),
    ("Golden Key 🔑", 350),
    ("Magic Potion 🧪", 500),
    ("Royal Crown 👑", 900),
]

TOOLS = [
    ("Wooden", 50),
    ("Stone", 150),
    ("Iron", 400),
    ("Gold", 1200),
    ("Platinum", 3000),
    ("Diamond", 8000),
    ("Emerald", 20000),
]



# ===========================================================
# SECTION BUTTONS (FIRST MENU)
# ===========================================================
def main_shop_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⭐ Items", callback_data="shop_items")],
            [InlineKeyboardButton("🛠 Tools", callback_data="shop_tools")],
        ]
    )



# ===========================================================
# ITEMS BUTTON LIST
# ===========================================================
def items_keyboard():
    rows = []
    row = []
    for name, _ in ITEMS:
        row.append(InlineKeyboardButton(name, callback_data=f"buy_item:{name}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton("⬅ Back", callback_data="shop_back")])
    return InlineKeyboardMarkup(rows)



# ===========================================================
# TOOLS BUTTON LIST
# ===========================================================
def tools_keyboard():
    rows = []
    row = []
    for name, _ in TOOLS:
        row.append(InlineKeyboardButton(name, callback_data=f"buy_tool:{name}"))
        if len(row) == 2:
            rows.append(row)
            row = []

    if row:
        rows.append(row)

    rows.append([InlineKeyboardButton("⬅ Back", callback_data="shop_back")])
    return InlineKeyboardMarkup(rows)



# ===========================================================
# PURCHASE HELPERS
# ===========================================================
async def purchase_item(msg, user, name, price):
    if user["bronze"] < price:
        return await msg.reply(
            f"❌ Not enough Bronze.\nNeeded: {price}\nYou have: {user['bronze']}"
        )

    user["bronze"] -= price
    user["inventory"]["items"].append(name)

    update_user(user["_id"], {
        "bronze": user["bronze"],
        "inventory": user["inventory"]
    })

    await msg.reply(f"✅ **Purchased:** {name}\nRemaining Bronze: {user['bronze']}")


async def purchase_tool(msg, user, name, price):

    if user["bronze"] < price:
        return await msg.reply(
            f"❌ Not enough Bronze.\nNeeded: {price}\nYou have: {user['bronze']}"
        )

    user["bronze"] -= price
    user["tools"][name] = user["tools"].get(name, 0) + 1

    # set durability
    from games.mine import TOOLS as MINE_TOOLS
    user["tool_durabilities"][name] = MINE_TOOLS[name]["durability"]

    update_user(user["_id"], {
        "bronze": user["bronze"],
        "tools": user["tools"],
        "tool_durabilities": user["tool_durabilities"]
    })

    await msg.reply(
        f"🛠 **Purchased Tool:** {name}\n"
        f"Use `/equip {name}` to equip it.\n"
        f"Remaining Bronze: {user['bronze']}"
    )



# ===========================================================
# INIT SHOP
# ===========================================================
def init_shop(bot: Client):

    # ---------------------------
    # /shop
    # ---------------------------
    @bot.on_message(filters.command("shop"))
    async def open_shop(_, msg: Message):

        await msg.reply(
            "🛒 **GAMEBOT SHOP**\n\n"
            "Choose a section below:",
            reply_markup=main_shop_keyboard()
        )

    # ---------------------------
    # TEXT BUY /buy item name
    # ---------------------------
    @bot.on_message(filters.command("buy"))
    async def text_buy(_, msg: Message):

        if len(msg.text.split()) < 2:
            return await msg.reply("Usage:\n`/buy Lucky Charm`")

        query = msg.text.split(maxsplit=1)[1].strip().lower()
        user = get_user(msg.from_user.id)

        # items
        for name, price in ITEMS:
            if name.lower() == query:
                return await purchase_item(msg, user, name, price)

        # tools
        for name, price in TOOLS:
            if name.lower() == query:
                return await purchase_tool(msg, user, name, price)

        return await msg.reply("❌ Item not found. Use /shop")



    # ===========================================================
    # SECTION SWITCHES (buttons)
    # ===========================================================
    @bot.on_callback_query(filters.regex("shop_items"))
    async def show_items(_, cq: CallbackQuery):
        await cq.message.edit_text(
            "🛒 **Items Store**\nSelect an item to buy:",
            reply_markup=items_keyboard()
        )
        await cq.answer()


    @bot.on_callback_query(filters.regex("shop_tools"))
    async def show_tools(_, cq: CallbackQuery):
        await cq.message.edit_text(
            "🛠 **Tools Store**\nSelect a tool to buy:",
            reply_markup=tools_keyboard()
        )
        await cq.answer()


    @bot.on_callback_query(filters.regex("shop_back"))
    async def back_to_main(_, cq: CallbackQuery):
        await cq.message.edit_text(
            "🛒 **GAMEBOT SHOP**\nChoose a section:",
            reply_markup=main_shop_keyboard()
        )
        await cq.answer()



    # ===========================================================
    # BUTTON BUY HANDLERS
    # ===========================================================
    @bot.on_callback_query(filters.regex(r"^buy_item:"))
    async def buy_item_button(_, cq: CallbackQuery):

        name = cq.data.split(":", 1)[1]
        price = next(p for n, p in ITEMS if n == name)
        user = get_user(cq.from_user.id)

        await purchase_item(cq.message, user, name, price)
        await cq.answer()


    @bot.on_callback_query(filters.regex(r"^buy_tool:"))
    async def buy_tool_button(_, cq: CallbackQuery):

        name = cq.data.split(":", 1)[1]
        price = next(p for n, p in TOOLS if n == name)
        user = get_user(cq.from_user.id)

        await purchase_tool(cq.message, user, name, price)
        await cq.answer()


    print("[loaded] games.shop")
