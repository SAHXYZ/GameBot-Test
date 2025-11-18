from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI")

# ---- FIX: Allow TLS on Heroku ----
client = MongoClient(
    MONGO_URI,
    tls=True,
    tlsAllowInvalidCertificates=True
)

db = client["GameBot"]
users = db["users"]


# ----------------------------------
# Fetch or Create User
# ----------------------------------
def get_user(user_id):
    user_id = str(user_id)
    user = users.find_one({"_id": user_id})

    # If user does not exist, create full schema
    if not user:
        user = {
            "_id": user_id,

            # --- COINS ---
            "black_gold": 0,
            "platinum": 0,
            "gold": 0,
            "silver": 0,
            "bronze": 0,

            # --- STATS ---
            "messages": 0,
            "fight_wins": 0,
            "rob_success": 0,
            "rob_fail": 0,

            # --- OTHER ---
            "cooldowns": {},
            "inventory": [],
            "badges": []
        }
        users.insert_one(user)

    return user


# ----------------------------------
# Update user
# ----------------------------------
def update_user(user_id, data: dict):
    users.update_one(
        {"_id": str(user_id)},
        {"$set": data},
        upsert=True
    )
