# games/shop.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database.mongo import get_user, update_user

# Example shop: both items and tools. Tools are identified by name in TOOLS above.
SHOP_ITEMS = [
    ("Lucky Charm 🍀", 200, "item"),
    ("Golden Key 🔑", 350, "item"),
    ("Magic Potion 🧪", 500, "item"),
    ("Royal Crown 👑", 900, "item"),
    # Tools (name must match TOOLS keys in games/mine.py)
    ("Wooden", 50, "tool"),
    ("Stone", 150, "tool"),
    ("Iron", 400, "tool"),
    ("Gold", 1200, "tool"),
    ("Platinum", 3000, "tool"),
    ("Diamond", 8000, "tool"),
    ("Emerald", 20000, "tool"),
]


def init_shop(bot: Client):

    @bot.on_message(filters.command("shop"))
    async def shop_cmd(_, msg: Message):
        lines = ["🛒 Shop Items:\n"]
        for i, (name, price, typ) in enumerate(SHOP_ITEMS, start=1):
            label = "Tool" if typ == "tool" else "Item"
            lines.append(f"{i}. {name} — {price} Bronze 🥉 ({label})")
        lines.append("\nBuy with: /buy <number>  OR /buy <name>")
        await msg.reply("\n".join(lines))

    @bot.on_message(filters.command("buy"))
    async def buy_cmd(_, msg: Message):
        if not msg.from_user:
            return

        parts = msg.text.split(maxsplit=1)
        if len(parts) < 2:
            return await msg.reply("Usage: /buy <item_number_or_name>")

        query = parts[1].strip()
        # try numeric index first
        choice = None
        try:
            idx = int(query) - 1
            if 0 <= idx < len(SHOP_ITEMS):
                choice = SHOP_ITEMS[idx]
        except:
            pass

        if choice is None:
            # try match by name (case-insensitive)
            for name, price, typ in SHOP_ITEMS:
                if name.lower() == query.lower():
                    choice = (name, price, typ)
                    break

        if choice is None:
            return await msg.reply("❌ Item not found. Use /shop to see available items.")

        name, price, typ = choice
        user = get_user(msg.from_user.id)
        bronze = user.get("bronze", 0)

        if bronze < price:
            return await msg.reply(f"❌ You need {price} Bronze to buy {name}. You have {bronze} Bronze.")

        # Deduct price and add to inventory/tools
        user["bronze"] = bronze - price

        if typ == "item":
            inv = user.setdefault("inventory", {})
            items = inv.setdefault("items", [])
            items.append(name)
            # optional badge
            badges = user.setdefault("badges", [])
            if len(items) >= 5 and "🛍️" not in badges:
                badges.append("🛍️")
            update_user(msg.from_user.id, {"bronze": user["bronze"], "inventory": inv, "badges": badges})
            return await msg.reply(f"✅ Purchased {name}. Remaining Bronze: {user['bronze']}")

        else:  # tool
            tools = user.setdefault("tools", {})
            count = tools.get(name, 0) + 1
            tools[name] = count
            # ensure durability entry exists
            td = user.setdefault("tool_durabilities", {})
            # use default durability by checking TOOLS structure used in mine.py
            # if not present, default to 100 durability
            default_dur = 100
            try:
                # try to import TOOLS from games.mine if available
                from games.mine import TOOLS as _TOOLS
                default_dur = _TOOLS.get(name, {}).get("durability", default_dur)
            except Exception:
                pass

            td.setdefault(name, default_dur)
            update_user(msg.from_user.id, {"bronze": user["bronze"], "tools": tools, "tool_durabilities": td})
            return await msg.reply(f"✅ Purchased tool {name}. Use /equip {name} to equip it. Remaining Bronze: {user['bronze']}")
