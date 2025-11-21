# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import random

from database.mongo import get_user, update_user

# ---------------------------------------------------------
# 🎁 DAILY REWARD VALUES
# ---------------------------------------------------------
BRONZE_REWARD = 100

def random_crate():
    """7th-day crate: weighted probabilities."""
    roll = random.random() * 100  # 0 - 100

    if roll <= 80:
        return ("1000 Bronze Coins", {"bronze": 1000})
    elif roll <= 95:
        return ("100 Silver Coins", {"silver": 100})
    else:
        gold = random.randint(1, 50)
        return (f"{gold} Gold Coins", {"gold": gold})


# ---------------------------------------------------------
# 📌 INIT DAILY HANDLER
# ---------------------------------------------------------
def init_daily(bot: Client):

    @bot.on_message(filters.command("daily"))
    async def daily_cmd(_, msg: Message):
        user_id = msg.from_user.id
        user = get_user(user_id)

        today = datetime.utcnow().date()
        last_claim = user.get("last_daily")
        
        # Convert stored date to datetime.date
        if last_claim:
            last_claim = datetime.strptime(last_claim, "%Y-%m-%d").date()

        streak = user.get("daily_streak", 0)

        # ---------------------------------------------------------
        # 🕒 FIRST CLAIM OR MISSED DAY → RESET
        # ---------------------------------------------------------
        if not last_claim or (today - last_claim).days > 1:
            streak = 1  # restart from day 1
            reward_msg = f"🎉 <b>Daily Login — Day 1</b>\nYou received <b>{BRONZE_REWARD} Bronze Coins</b>!"
            update_user(user_id, {"bronze": user.get("bronze", 0) + BRONZE_REWARD})

        # ---------------------------------------------------------
        # 📅 SAME DAY → Already claimed
        # ---------------------------------------------------------
        elif (today - last_claim).days == 0:
            await msg.reply(
                "⏳ <b>You already claimed your daily reward today!</b>\n"
                "Come back tomorrow for more rewards."
            )
            return

        # ---------------------------------------------------------
        # 🔥 CONTINUE STREAK
        # ---------------------------------------------------------
        else:
            streak += 1

            # Day 1 - 6: Bronze reward
            if streak < 7:
                reward_msg = (
                    f"🎉 <b>Daily Login — Day {streak}</b>\n"
                    f"You received <b>{BRONZE_REWARD} Bronze Coins</b>!"
                )
                update_user(user_id, {"bronze": user.get("bronze", 0) + BRONZE_REWARD})

            # Day 7 → Random Crate
            else:
                crate_name, reward = random_crate()
                reward_msg = (
                    f"🎁 <b>Daily Login — Day 7</b>\n"
                    f"✨ <b>Random Crate Reward:</b> {crate_name}!\n\n"
                    f"Your streak resets tomorrow."
                )

                # Apply crate reward
                for k, v in reward.items():
                    update_user(user_id, {k: user.get(k, 0) + v})

                # Reset streak after day 7
                streak = 0  

        # Save streak + last claim date
        update_user(user_id, {
            "daily_streak": streak,
            "last_daily": today.strftime("%Y-%m-%d")
        })

        await msg.reply(reward_msg)
