from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME", "GameBot")

client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client[DB_NAME]
users = db["users"]


def get_user(user_id):
    user_id = str(user_id)
    user = users.find_one({"_id": user_id})

    # ------------------------------
    # NEW USER (FIRST TIME)
    # ------------------------------
    if not user:
        user = {
            "_id": user_id,

            # currency system
            "black_gold": 0,
            "platinum": 0,
            "gold": 0,
            "silver": 0,
            "bronze": 0,

            # stats
            "messages": 0,
            "fight_wins": 0,
            "rob_success": 0,
            "rob_fail": 0,

            # cooldowns
            "cooldowns": {},

            # inventory format
            "inventory": {
                "ores": {},
                "items": []
            },

            # mining system fields
            "tools": {"Wooden": 1},
            "equipped": "Wooden",
            "tool_durabilities": {"Wooden": 50},
            "last_mine": 0,

            # badges
            "badges": []
        }

        users.insert_one(user)
        return user

    # ------------------------------
    # EXISTING USER — FIX STRUCTURE SAFELY
    # ------------------------------

    update_data = {}

    # inventory
    inv = user.get("inventory")
    if not isinstance(inv, dict):
        update_data["inventory"] = {"ores": {}, "items": []}
    else:
        update_data["inventory"] = inv
        update_data["inventory"].setdefault("ores", {})
        update_data["inventory"].setdefault("items", [])

    # mining fields
    update_data.setdefault("tools", user.get("tools", {"Wooden": 1}))
    update_data.setdefault("equipped", user.get("equipped", "Wooden"))
    update_data.setdefault("tool_durabilities", user.get("tool_durabilities", {"Wooden": 50}))
    update_data.setdefault("last_mine", user.get("last_mine", 0))

    # cooldowns
    update_data.setdefault("cooldowns", user.get("cooldowns", {}))

    # currencies
    for field in ["bronze", "silver", "gold", "platinum", "black_gold"]:
        update_data.setdefault(field, user.get(field, 0))

    # stats
    for field in ["messages", "fight_wins", "rob_success", "rob_fail"]:
        update_data.setdefault(field, user.get(field, 0))

    # badges
    update_data.setdefault("badges", user.get("badges", []))

    # Merge fixes
    users.update_one({"_id": user_id}, {"$set": update_data})

    # Return updated version
    user.update(update_data)
    return user


def update_user(user_id, data: dict):
    users.update_one(
        {"_id": str(user_id)},
        {"$set": data},
        upsert=True
    )
