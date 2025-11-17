# filename: games/shop.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db

SHOP_ITEMS = [
    ("Lucky Charm 🍀", 200),
    ("Golden Key 🔑", 350),
    ("Magic Potion 🧪", 500),
    ("Royal Crown 👑", 900),
]

def init_shop(bot: Client):
    @bot.on_message(filters.command("shop"))
    async def shop(_, msg: Message):
        if not msg.from_user:
            return
        text = "🛒 **Shop Items:**\n\n"
        for i,(name,price) in enumerate(SHOP_ITEMS, start=1):
            text += f"{i}. {name} — `{price}` coins\n"
        text += "\nUse /buy <item_number> to purchase."
        await msg.reply(text)

    @bot.on_message(filters.command("buy"))
    async def buy(_, msg: Message):
        if not msg.from_user:
            return
        parts = msg.text.split()
        if len(parts) < 2:
            return await msg.reply("Usage: /buy <item_number>")
        try:
            idx = int(parts[1]) - 1
        except:
            return await msg.reply("Invalid item number.")

        if idx < 0 or idx >= len(SHOP_ITEMS):
            return await msg.reply("Invalid item number.")

        name, price = SHOP_ITEMS[idx]
        user = db.get_user(msg.from_user.id)
        if user.get('coins',0) < price:
            return await msg.reply("You don't have enough coins to buy this item.")

        user['coins'] = user.get('coins',0) - price
        inv = user.get('inventory', [])
        inv.append(name)
        user['inventory'] = inv
        # badge
        badges = user.get('badges', [])
        if len(inv) >= 5 and '🛍️' not in badges:
            badges.append('🛍️')
        user['badges'] = badges

        db.update_user(msg.from_user.id, user)
        await msg.reply(f"✅ Purchased {name}. Remaining coins: `{user['coins']}`")
