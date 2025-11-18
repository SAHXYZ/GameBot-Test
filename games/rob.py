# filename: games/rob.py
from pyrogram import Client, filters
from pyrogram.types import Message
from database_main import db
from utils.cooldown import check_cooldown, update_cooldown
import random, asyncio


def init_rob(bot: Client):

    @bot.on_message(filters.command("rob"))
    async def rob_game(_, msg: Message):
        if not msg.from_user:
            return

        # Must reply to a user to rob
        if not msg.reply_to_message or not msg.reply_to_message.from_user:
            return await msg.reply("Reply to a user to rob them!")

        robber = msg.from_user
        victim = msg.reply_to_message.from_user

        if robber.id == victim.id:
            return await msg.reply("You cannot rob yourself.")

        robber_data = db.get_user(robber.id)
        victim_data = db.get_user(victim.id)

        ok, wait, pretty = check_cooldown(robber_data, "rob", 300)
        if not ok:
            return await msg.reply(f"⏳ You must wait **{pretty}** before robbing again.")

        rob_msg = await msg.reply("🕵️ Trying to rob...")
        await asyncio.sleep(1)

        # ---------------------------
        # STEP 1: Decide which coin tier to attempt
        # ---------------------------

        # AND REMOVE TIERS IF VICTIM HAS 0 IN THAT TIER
        chances = []

        # Bronze = 100% (ALWAYS allowed)
        if victim_data.get("bronze", 0) > 0:
            chances.append(("bronze", 100))

        # Silver = 80% chance
        if victim_data.get("silver", 0) > 0:
            chances.append(("silver", 80))

        # Gold = 50% chance
        if victim_data.get("gold", 0) > 0:
            chances.append(("gold", 50))

        # Platinum = 1% chance
        if victim_data.get("platinum", 0) > 0:
            chances.append(("platinum", 1))

        # If no coin tiers available
        if not chances:
            robber_data = update_cooldown(robber_data, "rob")
            db.update_user(robber.id, robber_data)
            return await rob_msg.edit("😶 Target has **no coins** to steal.")

        # Weighted tier selection
        # Example: [("gold", 50), ("silver", 80), ("bronze", 100)]
        tier_choices = [tier for tier, weight in chances]
        tier_weights = [weight for tier, weight in chances]

        chosen_tier = random.choices(tier_choices, weights=tier_weights, k=1)[0]

        # ---------------------------
        # STEP 2: Decide outcome (success/fail)
        # ---------------------------

        # Success chance = weight% (example: silver = 80% chance)
        if random.randint(1, 100) > [w for t, w in chances if t == chosen_tier][0]:
            # FAILED ROBBERY
            penalty = random.randint(1, 30)
            robber_data["bronze"] = max(0, robber_data.get("bronze", 0) - penalty)
            robber_data = update_cooldown(robber_data, "rob")

            db.update_user(robber.id, robber_data)

            return await rob_msg.edit(
                f"🚨 **Robbery Failed!**\n"
                f"You lost **-{penalty} Bronze 🥉** as a penalty."
            )

        # ---------------------------
        # STEP 3: SUCCESSFUL ROBBERY
        # ---------------------------

        if chosen_tier == "bronze":
            amount = random.randint(1, min(50, victim_data.get("bronze", 0)))
        elif chosen_tier == "silver":
            amount = random.randint(1, min(10, victim_data.get("silver", 0)))
        elif chosen_tier == "gold":
            amount = random.randint(1, min(5, victim_data.get("gold", 0)))
        elif chosen_tier == "platinum":
            amount = 1  # platinum is rare

        # Deduct from victim
        victim_data[chosen_tier] = max(0, victim_data.get(chosen_tier, 0) - amount)

        # Add to robber
        robber_data[chosen_tier] = robber_data.get(chosen_tier, 0) + amount

        # Update cooldown
        robber_data = update_cooldown(robber_data, "rob")

        # Save both
        db.update_user(robber.id, robber_data)
        db.update_user(victim.id, victim_data)

        # Tier icons
        tier_emoji = {
            "bronze": "🥉",
            "silver": "🥈",
            "gold": "🥇",
            "platinum": "🏅",
        }[chosen_tier]

        await rob_msg.edit(
            f"💰 **Robbery Successful!**\n"
            f"You stole **{amount} {tier_emoji} {chosen_tier.capitalize()}**\n"
            f"from **{victim.first_name}**!"
        )
