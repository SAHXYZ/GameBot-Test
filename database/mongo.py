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


# -------------------------------------------------
# DEFAULT USER STRUCTURE (Single Source of Truth)
# -------------------------------------------------
DEFAULT_USER = {
    "black_gold": 0,
    "platinum": 0,
    "gold": 0,
    "silver": 0,
    "bronze": 0,

    "messages": 0,
    "fight_wins": 0,
    "rob_success": 0,
    "rob_fail": 0,

    "cooldowns": {},

    "inventory": {
        "ores": {},
        "items": []
    },

    "tools": {"Wooden": 1},
    "equipped": "Wooden",
    "tool_durabilities": {"Wooden": 50},
    "last_mine": 0,

    "badges": []
}


# -------------------------------------------------
# GET USER + SAFELY FIX STRUCTURE
# -------------------------------------------------
def get_user(user_id):
    user_id = str(user_id)
    user = users.find_one({"_id": user_id})

    # --------------- CREATE NEW USER ---------------
    if not user:
        new_user = {"_id": user_id}
        new_user.update(DEFAULT_USER)
        users.insert_one(new_user)
        return new_user

    # --------------- FIX EXISTING USER ---------------
    updated = False
    fixed_user = {"_id": user_id}

    # merge defaults + existing values
    for key, default_value in DEFAULT_USER.items():
        if key not in user:
            fixed_user[key] = default_value
            updated = True
        else:
            # deep fix for nested inventory
            if key == "inventory":
                inv = user.get("inventory", {})

                if not isinstance(inv, dict):
                    inv = {"ores": {}, "items": []}
                    updated = True

                inv.setdefault("ores", {})
                inv.setdefault("items", [])

                fixed_user[key] = inv

                if inv != user.get("inventory"):
                    updated = True

            else:
                fixed_user[key] = user[key]

    # If any corrections made → update DB
    if updated:
        users.update_one({"_id": user_id}, {"$set": fixed_user})

    return fixed_user


# -------------------------------------------------
# UPDATE USER
# -------------------------------------------------
def update_user(user_id, data: dict):
    users.update_one(
        {"_id": str(user_id)},
        {"$set": data},
        upsert=True
    )
