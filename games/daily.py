# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message
import time, random
from database.mongo import get_user, update_user


DAILY_COOLDOWN = 24 * 60 * 60
DAILY_MIN = 120
DAILY_MAX = 350

CRATES = [
    ("Bronze Crate", 65),    # 65% chance
    ("Silver Crate", 25),    # 25% chance
    ("Gold Crate", 8),       # 8% chance
    ("Diamond Crate", 2),    # 2% chance
]

RARE_ITEMS = [
    "⚡ Power Token",
    "💎 Crystal Shard",
    "🔥 Phoenix Feather",
    "🎯 Luck Stone",
    "🛡 Shield of Honor"
]


def pick_weighted(table):
    pool = []
    for item, weight in table:
        pool += [item] * weight
    return random.choice(pool)


def format_time(seconds: int):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    res = []
    if h: res.append(f"{h}h")
    if m: res.append(f"{m}m")
    if s or not res: res.append(f"{s}s")
    return " ".join(res)


async def daily_reward(uid: int, msg: Message):
    user = get_user(uid)

    if not user:
        await msg.reply("⚠️ No profile found. Use /start first.")
        return

    now = int(time.time())
    last = user.get("last_daily")

    # Cooldown
    if last:
        remaining = (last + DAILY_COOLDOWN) - now
        if remaining > 0:
            await msg.reply(f"⏳ Already claimed.\nCome back in **{format_time(remaining)}**.")
            return

    # Streak
    streak = user.get("daily_streak", 0)
    if last and now - last <= DAILY_COOLDOWN * 2:
        streak += 1
    else:
        streak = 1

    # Base Coins
    base = random.randint(DAILY_MIN, DAILY_MAX)
    bonus_pct = min(streak * 5, 50)
    bonus = (base * bonus_pct) // 100
    total_coins = base + bonus

    # Crate drop
    crate = pick_weighted(CRATES)

    # Rare Item chance (increases with streak)
    rare_item = None
    if random.random() < 0.05 + (streak * 0.01):  # streak boosts drop rate
        rare_item = random.choice(RARE_ITEMS)

    # Jackpot (super rare)
    jackpot = None
    if random.random() < 0.002:  # 0.2%
        jackpot = random.randint(5000, 15000)

    # Update database
    updates = {
        "coins": user.get("coins", 0) + total_coins,
        "last_daily": now,
        "daily_streak": streak,
    }

    # Items inventory creation
    user.setdefault("inventory", {})
    user["inventory"].setdefault("items", [])

    if rare_item:
        user["inventory"]["items"].append(rare_item)
        updates["inventory"] = user["inventory"]

    update_user(uid, updates)

    # Response message
    text = (
        f"🎁 **Daily Reward Claimed!**\n\n"
        f"💰 Base: **{base}** coins\n"
        f"🔥 Bonus: **+{bonus}** coins ({bonus_pct}%)\n"
        f"🏦 Total Earned: **{total_coins}** coins\n\n"
        f"📦 You received: **{crate}**"
    )

    if rare_item:
        text += f"\n✨ Rare Loot: **{rare_item}**"

    if jackpot:
        text += f"\n💸💥 **JACKPOT HIT!** +{jackpot} extra coins!"
        update_user(uid, {"coins": updates["coins"] + jackpot})

    text += f"\n\n📅 Streak: **{streak} days**"
    await msg.reply(text)


def init_daily(bot: Client):
    @bot.on_message(filters.command("daily"))
    async def _(c, m: Message):
        await daily_reward(m.from_user.id, m)
    print("[loaded] games.daily")
