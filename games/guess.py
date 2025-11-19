# guess.py
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

# ---- Config ----
WORDS_PATH = os.path.join("assets", "words.json")  # as requested
DEFAULT_WORDS = {"easy": {}, "medium": {}, "hard": {}}

# ---- Load words ----
def load_words(path=WORDS_PATH):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # ensure keys exist
            return {
                "easy": data.get("easy", {}),
                "medium": data.get("medium", {}),
                "hard": data.get("hard", {}),
            }
    except FileNotFoundError:
        print(f"[WARN] words.json not found at {path}. Using empty lists.")
        return DEFAULT_WORDS.copy()
    except Exception as e:
        print(f"[WARN] Failed to load {path}: {e}")
        return DEFAULT_WORDS.copy()

WORDS = load_words()

# ---- Per-chat quiz state ----
# chat_id (str) -> {
#   "difficulty": "easy"/"medium"/"hard",
#   "word": "currentword",
#   "hint": "hint text",
#   "answer_mode": False
# }
chats = {}

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

def pretty_hint(hint: str, word_len: int):
    return f"{hint}\n\n🔤 Letters: {word_len}"

# ---- Init function to register with the bot ----
def init_guess(bot: Client):
    """
    Call init_guess(bot) to register handlers.
    Expects `assets/words.json` to exist and be structured as:
    {
      "easy": { "apple": "hint", ... },
      "medium": { "planet": "hint", ... },
      "hard": { "crystal": "hint", ... }
    }
    """

    @bot.on_message(filters.command("guess"))
    async def cmd_guess(_, msg: Message):
        """
        Show difficulty selection buttons.
        If a quiz is already active in the chat, inform the user instead.
        """
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)
        if state and state.get("word"):
            await msg.reply(
                "⚠️ A quiz is already running in this chat.\n\n"
                "Use /answer to enable answering or /stop to end the quiz."
            )
            return

        await msg.reply("🧠 Choose quiz difficulty:", reply_markup=buttons_markup())

    @bot.on_callback_query(filters.regex(r"^guess_(easy|medium|hard)$"))
    async def on_difficulty(client: Client, cq: CallbackQuery):
        """
        Start a quiz for the selected difficulty. Only one quiz per chat.
        """
        level = cq.data.split("_", 1)[1]  # easy / medium / hard
        chat_id = str(cq.message.chat.id)

        # If a quiz is already running in this chat, inform the user
        state = chats.get(chat_id)
        if state and state.get("word"):
            await cq.answer("A quiz is already running. Use /stop to end it.", show_alert=True)
            return

        word, hint = pick_random_word(level)
        if not word:
            await cq.answer("No words available for this difficulty.", show_alert=True)
            return

        chats[chat_id] = {
            "difficulty": level,
            "word": word,
            "hint": hint,
            "answer_mode": False,
        }

        # Edit or reply with the hint and instructions
        try:
            await cq.message.edit_text(
                f"🧩 **New Quiz — {level.title()}**\n\n"
                f"🔎 **Hint:** {pretty_hint(hint, len(word))}\n\n"
                "📌 Use `/answer` to enable answering (everyone in chat can participate).\n"
                "▶ Use `/new` to get a new word (same difficulty).\n"
                "🛑 Use `/stop` to end the quiz.",
                parse_mode="md",
            )
        except Exception:
            # fallback in case edit fails (e.g., message no longer editable)
            await cq.message.reply_text(
                f"🧩 **New Quiz — {level.title()}**\n\n"
                f"🔎 **Hint:** {pretty_hint(hint, len(word))}\n\n"
                "📌 Use /answer to enable answering (everyone in chat can participate).\n"
                "▶ Use /new to get a new word (same difficulty).\n"
                "🛑 Use /stop to end the quiz."
            )

        await cq.answer()

    @bot.on_message(filters.command("answer"))
    async def cmd_answer(_, msg: Message):
        """
        Enable answer mode for the chat's current quiz.
        """
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)
        if not state or not state.get("word"):
            return await msg.reply("❌ No quiz running. Use /guess to start one.")
        if state.get("answer_mode"):
            return await msg.reply("✅ Answer mode is already enabled. Send your guess.")
        state["answer_mode"] = True
        await msg.reply("📝 **Answer mode ON!** Send your guesses as normal messages. Use /stop to end the quiz.")

    @bot.on_message(filters.command("new"))
    async def cmd_new(_, msg: Message):
        """
        Provide a new word of the same difficulty for the chat.
        Resets answer_mode to False (requires /answer again).
        """
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)
        if not state or not state.get("word"):
            return await msg.reply("❌ No active quiz. Use /guess to start.")
        cat = state["difficulty"]
        word, hint = pick_random_word(cat)
        if not word:
            return await msg.reply("No more words available in this difficulty.")
        state.update({"word": word, "hint": hint, "answer_mode": False})
        await msg.reply(f"🔎 **New Hint:** {pretty_hint(hint, len(word))}\n\nUse /answer to start answering.")

    @bot.on_message(filters.text & ~filters.command(["guess", "answer", "new", "stop"]))
    async def on_text(_, msg: Message):
        """
        Handle incoming plain-text messages as potential guesses when answer_mode is enabled.
        """
        chat_id = str(msg.chat.id)
        state = chats.get(chat_id)
        if not state or not state.get("word"):
            return  # no quiz running
        if not state.get("answer_mode"):
            return  # answer mode not enabled

        # Accept the message as a guess (normalized)
        guess = msg.text.strip().lower()
        correct = state["word"].strip().lower()

        if guess == correct:
            # reward flow
            reward = random.randint(50, 200)
            try:
                user = get_user(msg.from_user.id)
            except Exception:
                user = {}
            new_bronze = user.get("bronze", 0) + reward
            try:
                update_user(msg.from_user.id, {"bronze": new_bronze})
            except Exception:
                # fail-safe: do not crash if DB update fails
                pass

            winner = msg.from_user.mention if msg.from_user else "Someone"

            # reset chat quiz
            chats.pop(chat_id, None)

            await msg.reply(
                f"🎉 **Correct!**\n"
                f"🏆 Winner: {winner}\n"
                f"🎁 Reward: **{reward} Bronze 🥉**\n\n"
                "Use /guess to start a new quiz."
            )
        else:
            # gentle wrong-answer reply
            await msg.reply("❌ Wrong guess. Try again!")

    @bot.on_message(filters.command("stop"))
    async def cmd_stop(_, msg: Message):
        """
        Stop and clear the current quiz for the chat.
        """
        chat_id = str(msg.chat.id)
        if chats.get(chat_id) and chats[chat_id].get("word"):
            chats.pop(chat_id, None)
            return await msg.reply("🛑 **Quiz stopped successfully.**")
        return await msg.reply("There is no active quiz in this chat.")

    # Admin: reload words.json at runtime (only for bot owner)
    @bot.on_message(filters.command("reload_words") & filters.me)
    async def cmd_reload(_, msg: Message):
        global WORDS
        WORDS = load_words()
        await msg.reply("🔄 words.json reloaded.")

    # end init_guess
