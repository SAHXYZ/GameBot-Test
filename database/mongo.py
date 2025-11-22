# File: database/mongo.py
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
# DEFAULT USER TEMPLATE (Single Source of Truth)
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

    "badges": [],

    # DAILY SYSTEM — must be integers (not None)
    "daily_streak": 0,
    "last_daily": 0,          # <-- FIXED
}


# -------------------------------------------------
# GET USER (Load + Fix Structure Automatically)
# -------------------------------------------------
def get_user(user_id):
    user_id = str(user_id)
    user = users.find_one({"_id": user_id})

    # Create new user if not exists
    if not user:
        new_user = {"_id": user_id}
        new_user.update(DEFAULT_USER)
        users.insert_one(new_user)
        return new_user

    # Fix existing user if structure changed
    updated = False
    fixed_user = {"_id": user_id}

    for key, default_value in DEFAULT_USER.items():
        if key not in user:
            fixed_user[key] = default_value
            updated = True
            continue

        value = user[key]

        # Patch for old installs — last_daily was None
        if key == "last_daily" and (value is None):
            fixed_user[key] = 0
            updated = True
            continue

        # Deep fix for inventory
        if key == "inventory":
            if not isinstance(value, dict):
                value = {"ores": {}, "items": []}
                updated = True

            value.setdefault("ores", {})
            value.setdefault("items", [])

            fixed_user[key] = value
            continue

        fixed_user[key] = value

    # Save if modified
    if updated:
        users.update_one({"_id": user_id}, {"$set": fixed_user})

    return fixed_user


# -------------------------------------------------
# CREATE USER IF NOT EXISTS
# -------------------------------------------------
def create_user_if_not_exists(user_id, name):
    user_id = str(user_id)
    user = users.find_one({"_id": user_id})

    if user:
        return user

    new_user = {"_id": user_id}
    new_user.update(DEFAULT_USER)
    new_user["name"] = name

    users.insert_one(new_user)
    return new_user


# -------------------------------------------------
# UPDATE USER
# -------------------------------------------------
def update_user(user_id, data: dict):
    users.update_one(
        {"_id": str(user_id)},
        {"$set": data},
        upsert=True
    )
