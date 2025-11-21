# File: GameBot/games/daily.py

from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import random

from database.mongo import get_user, update_user


BRONZE_REWARD = 100


def random_crate():
    """Return (text, {reward}) with probabilities."""
    roll = random.random() * 100  # 0–100%

    if roll <= 80:
        return ("1000 Bronze Coins", {"bronze": 1000})
    elif roll <= 95:
        return ("100 Silver Coins", {"silver": 100})
    else:
        gold = random.randint(1, 50)
        return (f"{gold} Gold Coins", {"gold": gold})


def init_daily(bot: Client):

    @bot.on_message(filters.command("daily"))
    async def daily_cmd(_, msg: Message):

        user_id = msg.from_user.id
        data = get_user(user_id)

        streak = data.get("daily_streak", 0)
        last = data.get("last_daily")  # should be string YYYY-MM-DD

        # Today's date
        today = datetime.utcnow().date()

        # -------------------------------
        # Convert last_daily safely
        # -------------------------------
        if last:
            try:
                last_date = datetime.strptime(last, "%Y-%m-%d").date()
            except:
                last_date = None
        else:
            last_date = None

        # ================================================================
        # CASE 1 → Already claimed today
        # ================================================================
        if last_date == today:
            await msg.reply(
                "⏳ <b>You already claimed today!</b>\nCome back tomorrow."
            )
            return

        # ================================================================
        # CASE 2 → First time OR missed a day → reset to day 1
        # ================================================================
        if (not last_date) or ((today - last_date).days > 1):
            streak = 1
            reward_text = f"🎉 <b>Daily Login — Day 1</b>\nYou received <b>{BRONZE_REWARD} Bronze</b>!"

            new_bronze = data.get("bronze", 0) + BRONZE_REWARD
            update_user(user_id, {"bronze": new_bronze})

        # ================================================================
        # CASE 3 → Continue streak
        # ================================================================
        else:
            streak += 1

            # Day 2–6 → Bronze
            if streak < 7:
                reward_text = (
                    f"🎉 <b>Daily Login — Day {streak}</b>\n"
                    f"You received <b>{BRONZE_REWARD} Bronze</b>!"
                )

                new_bronze = data.get("bronze", 0) + BRONZE_REWARD
                update_user(user_id, {"bronze": new_bronze})

            # Day 7 → Crate
            else:
                crate_name, crate_reward = random_crate()

                reward_text = (
                    f"🎁 <b>Daily Login — Day 7</b>\n"
                    f"✨ Random Crate Reward: <b>{crate_name}</b>\n"
                    f"🔥 Your streak has been reset!"
                )

                # Re-load fresh user before applying crate rewards
                fresh = get_user(user_id)

                # Apply crate reward
                for k, v in crate_reward.items():
                    update_user(user_id, {k: fresh.get(k, 0) + v})

                streak = 0  # RESET after day 7

        # ================================================================
        # Save the new streak + date
        # ================================================================
        update_user(user_id, {
            "daily_streak": streak,
            "last_daily": today.strftime("%Y-%m-%d")
        })

        await msg.reply(reward_text)
