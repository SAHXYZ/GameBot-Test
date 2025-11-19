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

# ---- Paths for the 3 difficulty files ----
ASSETS_DIR = os.path.join("games", "assets")
EASY_PATH = os.path.join(ASSETS_DIR, "Easy.json")
MEDIUM_PATH = os.path.join(ASSETS_DIR, "Medium.json")
HARD_PATH = os.path.join(ASSETS_DIR, "Hard.json")

# ---- Load words from the 3 JSON files ----
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

WORDS = {
    "easy": load_json(EASY_PATH),
    "medium": load_json(MEDIUM_PATH),
    "hard": load_json(HARD_PATH),
}

# ---- Per-chat quiz state ----
chats = {}   # chat_id -> quiz state dictionary

# ---- Helpers ----
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

# ---- Init function ----
def init_guess(bot: Client):

    @bot.on_message(filters.command("guess"))
    async def cmd_guess(_, msg: Message):
        chat_id = str(msg.chat.id)

        if chat_id in chats and chats[chat_id].get("word"):
            return await msg.reply(
                "⚠️ A quiz is already running.\nUse /answer or /stop."
            )

        await msg.reply(
            "🧠 **Choose difficulty**:",
            reply_markup=buttons_markup()
        )

    @bot.on_callback_query(filters.regex(r"^guess_(easy|medium|hard)$"))
    async def difficulty_selected(_, cq: CallbackQuery):
        chat_id = str(cq.message.chat.id)
        difficulty = cq.data.split("_")[1]

        if chat_id in chats and chats[chat_id].get("word"):
            return await cq.answer("Quiz already running. Use /stop.", show_alert=True)

        word, hint = pick_random_word(difficulty)
        if not word:
            return await cq.answer(
                "❌ No words available for this category.",
                show_alert=True
            )

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
            "🛑 Use `/stop` to end the quiz.",
            parse_mode="markdown"
        )
        await cq.answer()

    @bot.on_message(filters.command("answer"))
    async def enable_answer(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)

        if not state or not state.get("word"):
            return await msg.reply("❌ No active quiz.")

        if state["answer_mode"]:
            return await msg.reply("📝 Answer mode already enabled.")

        state["answer_mode"] = True
        await msg.reply("📝 **Answer mode enabled!** Send your guesses.")

    @bot.on_message(filters.command("new"))
    async def new_word(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)

        if not state:
            return await msg.reply("❌ No active quiz.")

        difficulty = state["difficulty"]
        word, hint = pick_random_word(difficulty)

        if not word:
            return await msg.reply("No words available.")

        state.update({"word": word, "hint": hint, "answer_mode": False})

        await msg.reply(
            f"🔎 **New Hint:** {pretty_hint(hint, len(word))}\n\n"
            "Use /answer to enable answering."
        )

    @bot.on_message(filters.text & ~filters.command(["guess", "answer", "new", "stop"]))
    async def process_answer(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)

        if not state or not state.get("word") or not state.get("answer_mode"):
            return

        guess = msg.text.strip().lower()
        correct = state["word"].lower()

        if guess != correct:
            return await msg.reply("❌ Wrong answer! Try again.")

        reward = random.randint(50, 200)

        try:
            user = get_user(msg.from_user.id)
            update_user(msg.from_user.id, {"bronze": user.get("bronze", 0) + reward})
        except:
            pass

        winner = msg.from_user.mention

        chats.pop(chat_id, None)

        await msg.reply(
            f"🎉 **Correct!**\n"
            f"🏆 Winner: {winner}\n"
            f"🎁 Reward: **{reward} Bronze 🥉**\n\n"
            "Use /guess to play again."
        )

    @bot.on_message(filters.command("stop"))
    async def stop_quiz(_, msg: Message):
        chat_id = str(msg.chat.id)

        if chat_id in chats:
            chats.pop(chat_id)
            return await msg.reply("🛑 **Quiz stopped.**")

        await msg.reply("❌ No active quiz.")

    # Owner command to reload JSON files without restart
    @bot.on_message(filters.command("reload_words") & filters.me)
    async def reload_words(_, msg: Message):
        global WORDS
        WORDS = {
            "easy": load_json(EASY_PATH),
            "medium": load_json(MEDIUM_PATH),
            "hard": load_json(HARD_PATH),
        }
        await msg.reply("🔄 **Word lists reloaded!**")
