import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# MongoDB URI from Heroku Config Vars
MONGO_URI = os.getenv("MONGO_URI")   # example: mongodb+srv://user:pass@cluster.mongodb.net
DB_NAME = os.getenv("DB_NAME", "GameBot")  # default = GameBot
