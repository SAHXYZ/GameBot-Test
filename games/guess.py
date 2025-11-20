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
import time
from database.mongo import get_user, update_user

ASSETS_DIR = os.path.join("games", "assets")
EASY_PATH = os.path.join(ASSETS_DIR, "Easy.json")
MEDIUM_PATH = os.path.join(ASSETS_DIR, "Medium.json")
HARD_PATH = os.path.join(ASSETS_DIR, "Hard.json")


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

# chats keyed by chat_id (string) to allow group/pm quizzes independently
# each state: {
#   "difficulty": "easy"/"medium"/"hard",
#   "word": "apple",
#   "hint": "a fruit",
#   "starter_id": <user id who started>,
#   "answer_mode": False,
#   "started_at": timestamp
# }
chats = {}

# small per-user anti-spam for answers: { user_id: last_answer_time }
_last_answer = {}


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


def quiz_control_markup():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("▶ Answer", callback_data="guess_answer"),
                InlineKeyboardButton("🔁 New", callback_data="guess_new"),
                InlineKeyboardButton("🛑 Stop", callback_data="guess_stop"),
            ]
        ]
    )


def pretty_hint(hint: str, length: int):
    return f"{hint}\n\n🔤 Letters: {length}"


def reward_for_difficulty(diff: str) -> int:
    if diff == "easy":
        return random.randint(1, 50)
    if diff == "medium":
        return random.randint(1, 100)
    return random.randint(100, 200)


def can_answer(user_id: int, cooldown_seconds: int = 2) -> bool:
    now = time.time()
    last = _last_answer.get(user_id, 0)
    if now - last < cooldown_seconds:
        return False
    _last_answer[user_id] = now
    return True


def init_guess(bot: Client):

    @bot.on_message(filters.command("guess") & filters.private | filters.command("guess") & ~filters.private)
    async def cmd_guess(_, msg: Message):
        chat_id = str(msg.chat.id)
        if chat_id in chats and chats[chat_id].get("word"):
            return await msg.reply("⚠️ A quiz is already running here. Use the buttons or /stop.")
        await msg.reply("🧠 **Choose difficulty:**", reply_markup=buttons_markup())

    @bot.on_callback_query(filters.regex(r"^guess_(easy|medium|hard)$"))
    async def difficulty_selected(_, cq: CallbackQuery):
        chat_id = str(cq.message.chat.id)
        difficulty = cq.data.split("_")[1]

        if chat_id in chats and chats[chat_id].get("word"):
            await cq.answer("A quiz is already running. Use /stop or /new.", show_alert=True)
            return

        word, hint = pick_random_word(difficulty)
        if not word:
            await cq.answer("❌ No words found for this difficulty.", show_alert=True)
            return

        chats[chat_id] = {
            "difficulty": difficulty,
            "word": word,
            "hint": hint,
            "starter_id": cq.from_user.id if cq.from_user else None,
            "answer_mode": False,
            "started_at": time.time(),
        }

        await cq.message.edit_text(
            f"🧩 **New Quiz — {difficulty.title()} Mode**\n\n"
            f"🔎 **Hint:** {pretty_hint(hint, len(word))}\n\n"
            "Use the buttons below or commands:\n"
            "▶ /answer — enable answer mode\n"
            "▶ /new — new word\n"
            "▶ /stop — end quiz",
            reply_markup=quiz_control_markup()
        )
        await cq.answer()

    @bot.on_callback_query(filters.regex(r"^guess_answer$"))
    async def cb_enable_answer(_, cq: CallbackQuery):
        chat_id = str(cq.message.chat.id)
        state = chats.get(chat_id)
        if not state or not state.get("word"):
            await cq.answer("❌ No active quiz.", show_alert=True)
            return
        if state["answer_mode"]:
            await cq.answer("📝 Answer mode already ON.", show_alert=True)
            return
        state["answer_mode"] = True
        await cq.answer("📝 Answer mode ON!")
        try:
            await cq.message.edit_reply_markup(quiz_control_markup())
        except:
            pass

    @bot.on_callback_query(filters.regex(r"^guess_new$"))
    async def cb_new_word(_, cq: CallbackQuery):
        chat_id = str(cq.message.chat.id)
        state = chats.get(chat_id)
        if not state:
            await cq.answer("❌ No active quiz.", show_alert=True)
            return

        difficulty = state["difficulty"]
        word, hint = pick_random_word(difficulty)
        if not word:
            await cq.answer("❌ No more words available.", show_alert=True)
            return

        state.update({"word": word, "hint": hint, "answer_mode": False})
        await cq.message.edit_text(
            f"🔎 **New Hint:** {pretty_hint(hint, len(word))}\n\nUse /answer or press ▶ Answer to enable answering.",
            reply_markup=quiz_control_markup()
        )
        await cq.answer()

    @bot.on_callback_query(filters.regex(r"^guess_stop$"))
    async def cb_stop_quiz(_, cq: CallbackQuery):
        chat_id = str(cq.message.chat.id)
        state = chats.get(chat_id)
        if not state:
            await cq.answer("❌ No active quiz.", show_alert=True)
            return

        starter = state.get("starter_id")
        # only starter or chat admin can stop; allow starter or same user who pressed
        if cq.from_user and starter and cq.from_user.id != starter:
            await cq.answer("Only the user who started the quiz can stop it.", show_alert=True)
            return

        chats.pop(chat_id, None)
        try:
            await cq.message.edit("🛑 **Quiz stopped.**")
        except:
            pass
        await cq.answer()

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
            f"🔎 **New Hint:** {pretty_hint(hint, len(word))}\n\nUse /answer to enable answering.",
            reply_markup=quiz_control_markup()
        )

    @bot.on_message(filters.text & ~filters.command(["guess", "answer", "new", "stop"]))
    async def process_answer(_, msg: Message):
        # ignore bots
        if not msg.from_user or msg.from_user.is_bot:
            return

        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)
        if not state or not state.get("word") or not state.get("answer_mode"):
            return

        # owner-only stop/new: allow only starter to stop via commands (already implemented for button)
        # basic per-user anti-spam
        if not can_answer(msg.from_user.id):
            return await msg.reply("⏳ Slow down — you are answering too fast.")

        guess = msg.text.strip().lower()
        correct = state["word"].lower()
        difficulty = state["difficulty"]

        if guess != correct:
            return await msg.reply("❌ Wrong answer! Try again.")

        reward = reward_for_difficulty(difficulty)

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
            "▶ Use /guess to start a new quiz!"
        )

    @bot.on_message(filters.command("stop"))
    async def stop_quiz(_, msg: Message):
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)
        if not state:
            return await msg.reply("❌ No quiz is currently running.")
        starter = state.get("starter_id")
        if msg.from_user and starter and msg.from_user.id != starter:
            return await msg.reply("Only the user who started the quiz can stop it.")
        chats.pop(chat_id, None)
        await msg.reply("🛑 **Quiz stopped.**")

    @bot.on_message(filters.command("reload_words") & filters.me)
    async def reload_words(_, msg: Message):
        global WORDS
        WORDS = {
            "easy": load_json(EASY_PATH),
            "medium": load_json(MEDIUM_PATH),
            "hard": load_json(HARD_PATH),
        }
        await msg.reply("🔄 **Word lists reloaded!**")
