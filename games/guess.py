from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
import json
import random
import os
from database.mongo import get_user, update_user

# -------- Paths for difficulty JSON files --------
ASSETS_DIR = os.path.join("games", "assets")
EASY_PATH = os.path.join(ASSETS_DIR, "Easy.json")
MEDIUM_PATH = os.path.join(ASSETS_DIR, "Medium.json")
HARD_PATH = os.path.join(ASSETS_DIR, "Hard.json")

# -------- Load JSON helper --------
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# -------- Load all words --------
WORDS = {
    "easy": load_json(EASY_PATH),
    "medium": load_json(MEDIUM_PATH),
    "hard": load_json(HARD_PATH),
}

# -------- Store quiz state per chat --------
# chats[chat_id] = { difficulty, word, hint, answer_mode }
chats = {}

# -------- Helpers --------
def pick_random_word(category: str):
    pool = WORDS.get(category, {})
    if not pool:
        return None, None

    word = random.choice(list(pool.keys()))
    return word, pool[word]

def buttons_markup():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("Easy", callback_data="guess_easy"),
                InlineKeyboardButton("Medium", callback_data="guess_medium"),
                InlineKeyboardButton("Hard", callback_data="guess_hard"),
            ]
        ]
    )

def pretty_hint(hint: str, length: int):
    return f"{hint}\n\n🔤 Letters: {length}"

# ---------------------------------------------------
# INIT FUNCTION
# ---------------------------------------------------
def init_guess(bot: Client):

    # ---------------------------- /guess ----------------------------
    @bot.on_message(filters.command("guess"))
    async def cmd_guess(_, msg: Message):
        chat_id = str(msg.chat.id)

        if chat_id in chats and chats[chat_id].get("word"):
            return await msg.reply(
                "⚠️ A quiz is already running.\nUse /answer or /stop."
            )

        await msg.reply(
            "🧠 **Choose difficulty:**",
            reply_markup=buttons_markup()
        )

    # ------------------- Difficulty selection (buttons) -------------------
    @bot.on_callback_query(filters.regex(r"^guess_(easy|medium|hard)$"))
    async def difficulty_selected(_, cq: CallbackQuery):
        chat_id = str(cq.message.chat.id)
        difficulty = cq.data.split("_")[1]

        if chat_id in chats and chats[chat_id].get("word"):
            return await cq.answer("Quiz already running. Use /stop.", show_alert=True)

        word, hint = pick_random_word(difficulty)
        if not word:
            return await cq.answer("❌ No words found for this difficulty.", show_alert=True)

        chats[chat_id] = {
            "difficulty": difficulty,
            "word": word,
            "hint": hint,
            "answer_mode": False,
        }

        await cq.message.edit_text(
            f"🧩 **New Quiz — {difficulty.title()} Mode**\n\n"
            f"🔎 **Hint:** {pretty_hint(hint, len(word))}\n\n"
            "📌 Use `/answer` to start answering.\n"
            "▶ Use `/new` to get a new word.\n"
            "🛑 Use `/stop` to end the quiz."
        )
        await cq.answer()

    # ---------------------------- /answer ----------------------------
    @bot.on_message(filters.command("answer"))
    async def enable_answer(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)

        if not state or not state.get("word"):
            return await msg.reply("❌ No active quiz.")

        if state["answer_mode"]:
            return await msg.reply("📝 Answer mode is already enabled.")

        state["answer_mode"] = True
        await msg.reply("📝 **Answer mode ON!** Send your guesses now.")

    # ---------------------------- /new ----------------------------
    @bot.on_message(filters.command("new"))
    async def new_word(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)

        if not state:
            return await msg.reply("❌ No active quiz running.")

        difficulty = state["difficulty"]
        word, hint = pick_random_word(difficulty)

        if not word:
            return await msg.reply("❌ No more words available.")

        state.update({"word": word, "hint": hint, "answer_mode": False})

        await msg.reply(
            f"🔎 **New Hint:** {pretty_hint(hint, len(word))}\n\n"
            "Use /answer to enable answering."
        )

    # ---------------------------- Guess handling ----------------------------
    @bot.on_message(filters.text & ~filters.command(["guess", "answer", "new", "stop"]))
    async def process_answer(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)

        if not state or not state.get("word") or not state.get("answer_mode"):
            return

        guess = msg.text.strip().lower()
        correct = state["word"].lower()
        difficulty = state["difficulty"]

        if guess != correct:
            return await msg.reply("❌ Wrong answer! Try again.")

        # ------------------ Difficulty-based rewards ------------------
        if difficulty == "easy":
            reward = random.randint(1, 50)
        elif difficulty == "medium":
            reward = random.randint(1, 100)
        else:  # hard
            reward = random.randint(100, 200)

        # Update database safely
        try:
            user = get_user(msg.from_user.id)
            update_user(
                msg.from_user.id,
                {"bronze": user.get("bronze", 0) + reward}
            )
        except:
            pass

        winner = msg.from_user.mention
        chats.pop(chat_id, None)

        await msg.reply(
            f"🎉 **Correct!**\n"
            f"🏆 Winner: {winner}\n"
            f"🎁 Reward: **{reward} Bronze 🥉**\n\n"
            "▶ Use /new for the next word!"
        )

    # ---------------------------- /stop ----------------------------
    @bot.on_message(filters.command("stop"))
    async def stop_quiz(_, msg: Message):
        chat_id = str(msg.chat.id)

        if chat_id in chats:
            chats.pop(chat_id)
            return await msg.reply("🛑 **Quiz stopped.**")

        await msg.reply("❌ No quiz is currently running.")

    # ---------------------------- Owner reload ----------------------------
    @bot.on_message(filters.command("reload_words") & filters.me)
    async def reload_words(_, msg: Message):
        global WORDS
        WORDS = {
            "easy": load_json(EASY_PATH),
            "medium": load_json(MEDIUM_PATH),
            "hard": load_json(HARD_PATH),
        }
        await msg.reply("🔄 **Word lists reloaded!**")
