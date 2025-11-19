from pyrogram import Client, filters
from pyrogram.types import Message
import random
from database.mongo import get_user, update_user

# -----------------------------------------
# WORDS + HINTS
# -----------------------------------------

HINTS = {
    "apple": "A popular fruit that keeps doctors away.",
    "grape": "A small juicy fruit often used to make wine.",
    "bread": "A staple food made by baking dough.",
    "chair": "A piece of furniture used for sitting.",
    "table": "A flat surface supported by legs.",
    "house": "A building where people live.",
    "light": "A source that makes things visible.",
    "heart": "The organ that pumps blood in the body.",
    "ocean": "A vast body of saltwater.",
    "earth": "The planet we live on.",
    "water": "A colorless liquid essential for life.",
    "smile": "A facial expression showing happiness.",
    "laugh": "A sound expressing joy or amusement.",
    "dream": "A series of thoughts during sleep.",
    "flame": "The bright, glowing part of a fire.",
    "beach": "A sandy area by the sea.",
    "grass": "Green plants covering the ground.",
    "cloud": "A mass of water vapor in the sky.",
    "storm": "A violent weather condition.",
    "peace": "A state without conflict.",
    "music": "Art made from sounds and rhythm.",
    "voice": "Sound produced when speaking.",
    "sound": "Vibrations that can be heard.",
    "stone": "A hard solid piece of mineral.",
    "river": "A natural stream of flowing water.",
    "mount": "To climb or rise onto something.",
    "plant": "A living organism that grows in soil.",
    "flour": "Powder made from grinding grains.",
    "wheat": "A grain used to make bread.",
    "angel": "A heavenly spiritual being.",
    "devil": "An evil or fallen angel.",
    "brave": "Showing courage in danger.",
    "happy": "Feeling joy or contentment.",
    "sadly": "In a sorrowful way.",
    "pride": "Satisfaction in achievements.",
    "crowd": "A large group of people.",
    "night": "The dark part of a day.",
    "early": "Before the usual time.",
    "later": "After the expected time.",
    "space": "The universe beyond Earth.",
    "speed": "How fast something moves.",
    "green": "The color of fresh grass.",
    "black": "The darkest color.",
    "white": "The lightest color.",
    "brown": "A color between red and yellow.",
    "clear": "Easy to understand or transparent.",
    "world": "Earth and everything in it.",
    "faith": "Strong belief or trust.",
    "honor": "High respect or esteem.",
    "glory": "Fame achieved by notable actions.",
    "fancy": "To imagine or desire something.",
    "forest": "A large area covered with trees.",
    "desert": "A dry area with very little rain.",
    "island": "Land surrounded by water.",
    "jungle": "A dense, tropical forest.",
    "stormy": "Full of heavy wind and rain.",
    "sunset": "Time when the sun goes down.",
    "sunrise": "Time when the sun comes up.",
    "shadow": "A dark shape made by blocking light.",
    "mirror": "Reflects your image.",
    "window": "An opening in a wall used to see outside.",
    "pillow": "Soft cushion used to rest your head.",
    "blanket": "A warm cover used during sleep.",
    "kettle": "A container used for boiling water.",
    "bottle": "A container typically used for liquids.",
    "bucket": "A round open container with a handle.",
    "basket": "A container woven out of flexible materials.",
    "orange": "A citrus fruit known for vitamin C.",
    "banana": "A yellow curved fruit rich in potassium.",
    "mango": "A sweet tropical fruit known as king of fruits.",
    "papaya": "A tropical fruit with orange flesh.",
    "candle": "A stick of wax that gives light when lit.",
    "camera": "A device used to capture photographs.",
    "mobile": "A handheld device used for communication.",
    "laptop": "A portable personal computer.",
    "pencil": "A writing tool made of graphite.",
    "marker": "A pen with thick colored ink.",
    "paper": "Thin material used for writing or printing.",
    "notebook": "A book of blank pages for writing.",
    "school": "A place where students learn.",
    "teacher": "A person who educates others.",
    "student": "A person who studies or learns.",
    "doctor": "A person who treats illnesses.",
    "nurse": "Someone who cares for people in hospitals.",
    "rocket": "A vehicle designed to travel into space.",
    "planet": "A large object orbiting a star.",
    "galaxy": "A massive system of stars and planets.",
    "comet": "A space object made of ice and dust.",
    "meteor": "A rock from space that burns in the atmosphere.",
    "engine": "A machine that produces power.",
    "helmet": "Protection worn on the head.",
    "wallet": "A small case for holding money.",
    "pocket": "A small pouch sewn into clothing.",
    "button": "A small object used to fasten clothing.",
    "jacket": "A piece of clothing worn to keep warm.",
    "ladder": "A tool used to reach high places.",
    "bridge": "A structure allowing passage over obstacles.",
    "harbor": "A safe place for ships to anchor.",
    "castle": "A large fortified ancient building.",
    "armor": "Protective covering worn in battle.",
    "shield": "A defensive item used to block attacks.",
    "sword": "A long-bladed weapon used for fighting.",
    "arrow": "A sharp projectile shot from a bow.",
    "hunter": "One who tracks and captures animals.",
    "farmer": "A person who grows crops or raises animals.",
    "builder": "Someone who constructs buildings.",
    "driver": "A person who operates a vehicle.",
    "sailor": "One who works on a boat or ship.",
    "captain": "A leader of a ship or team.",
    "leader": "Someone who guides others.",
    "king": "A male ruler of a kingdom.",
    "queen": "A female ruler of a kingdom.",
    "prince": "A male royal family member.",
    "princess": "A female royal family member.",
    "monkey": "A playful animal that climbs trees.",
    "tiger": "A large striped wild cat.",
    "lion": "A powerful big cat known as king of the jungle.",
    "horse": "An animal often used for riding.",
    "rabbit": "A small animal with long ears.",
    "mouse": "A tiny rodent attracted to food.",
    "eagle": "A bird known for sharp eyesight.",
    "parrot": "A bird that can mimic speech.",
    "pigeon": "A common city bird.",
    "spider": "A creature with eight legs.",
    "snake": "A legless reptile that slithers.",
    "shark": "A large predatory fish.",
    "dolphin": "A smart, playful marine animal.",
    "whale": "One of the largest mammals alive.",
    "zebra": "A striped black-and-white animal.",
    "camel": "A desert animal with humps.",
    "sheep": "A wool-producing farm animal.",
    "goat": "A farm animal known for climbing.",
    "crow": "A black bird known for intelligence.",
    "elevator": "A machine used to move people between floors.",
    "stairs": "Steps used for climbing.",
    "escalator": "Moving stairs.",
    "kitchen": "A room where food is prepared.",
    "bedroom": "A room where people sleep.",
    "bathroom": "A room with toilet and shower.",
    "garden": "An outdoor area with plants.",
    "garage": "A place to park vehicles.",
    "factory": "A building where products are made.",
    "library": "A place full of books.",
    "station": "A place where trains or buses stop.",
    "airport": "A place where airplanes take off.",
    "stadium": "A venue for sports.",
    "theater": "A place to watch movies or plays.",
    "cookie": "A small sweet baked treat.",
    "butter": "A dairy product used for cooking.",
    "cheese": "A dairy food from milk curds.",
    "honey": "A sweet substance made by bees.",
    "sugar": "A sweet substance.",
    "salt": "Seasoning mineral.",
    "pepper": "A spice.",
    "chicken": "A type of poultry meat.",
    "pizza": "Dough with sauce and cheese.",
    "burger": "Patty between buns.",
    "noodle": "Thin long dough pieces.",
    "pasta": "Italian noodles.",
    "salad": "Mixed vegetables.",
    "soup": "Liquid dish.",
    "steak": "Thick cut of beef.",
    "bacon": "Salt-cured meat.",
    "coffee": "Hot drink from beans.",
    "tea": "Beverage from steeped leaves.",
    "juice": "Liquid from fruits.",
    "milk": "White liquid from mammals.",
    "chocolate": "Sweet from cocoa.",
    "cereal": "Grains for breakfast.",
    "avocado": "Creamy green fruit.",
    "carrot": "Orange root vegetable.",
    "tomato": "Red fruit used in salads.",
    "potato": "Starchy vegetable.",
    "onion": "Strong-smelling vegetable.",
    "peppermint": "Cool herb.",
    "ginger": "Spicy root.",
    "garlic": "Strong-smelling bulb.",
    "cucumber": "Long green vegetable.",
    "pumpkin": "Large orange vegetable.",
    "coconut": "Hard-shelled tropical fruit.",
    "dragon": "Mythical fire-breathing creature.",
    "wizard": "Magic user.",
    "witch": "Person with magical powers.",
    "ghost": "Spirit of a dead person.",
    "zombie": "Reanimated corpse.",
    "robot": "Mechanical machine.",
    "alien": "Creature from another planet.",
    "giant": "Very large human-like creature.",
    "knight": "Armored medieval fighter.",
    "archer": "Bow-and-arrow expert.",
    "villain": "Story's bad character.",
    "hero": "Main character who saves the day.",
    "portal": "Door to another world.",
    "crystal": "Transparent mineral.",
    "treasure": "Valuable items."
}

WORD_LIST = list(HINTS.keys())

# -----------------------------------------
# GLOBAL QUIZ STORAGE
# -----------------------------------------
current_quiz = {
    "word": None,
    "hint": None,
    "answer_mode": False
}

# -----------------------------------------
# INIT FUNCTION
# -----------------------------------------
def init_guess(bot: Client):

    @bot.on_message(filters.command("guess"))
    async def start_quiz(_, msg: Message):
        if current_quiz["word"] is not None:
            return await msg.reply(
                "⚠️ **A quiz is already running in this chat!**\n\n"
                "Use **/answer** to participate.\n"
                "Or use **/stop** to end the current quiz before starting a new one. 🛑"
            )

        word = random.choice(WORD_LIST)
        hint = HINTS[word]

        current_quiz["word"] = word
        current_quiz["hint"] = hint
        current_quiz["answer_mode"] = False

        await msg.reply(
            f"🧩 **New Guess Quiz Started!**\n\n"
            f"🔎 **Hint:** {hint}\n\n"
            f"Use **/answer** to start guessing!"
        )

    @bot.on_message(filters.command("answer"))
    async def enable_answer(_, msg: Message):
        if current_quiz["word"] is None:
            return await msg.reply("❌ No quiz running.\nUse **/guess** to start one.")

        current_quiz["answer_mode"] = True

        await msg.reply(
            "📝 **Answer Mode Enabled!**\n"
            "Send your guesses now!\n"
            "Use /stop to end the quiz."
        )

    @bot.on_message(filters.text & ~filters.command(["guess", "answer", "stop"]))
    async def check_answer(_, msg: Message):

        if current_quiz["word"] is None:
            return

        if not current_quiz["answer_mode"]:
            return

        guess = msg.text.strip().lower()
        correct = current_quiz["word"]

        if guess == correct:

            reward = random.randint(50, 200)

            user = get_user(msg.from_user.id)
            new_bronze = user.get("bronze", 0) + reward
            update_user(msg.from_user.id, {"bronze": new_bronze})

            winner = msg.from_user.mention

            # Reset quiz
            current_quiz["word"] = None
            current_quiz["hint"] = None
            current_quiz["answer_mode"] = False

            return await msg.reply(
                f"🎉 **Correct Answer!**\n"
                f"🏆 Winner: {winner}\n"
                f"🎁 Reward: **{reward} Bronze 🥉**"
            )

        await msg.reply("❌ Wrong guess! Try again.")

    @bot.on_message(filters.command("stop"))
    async def stop_quiz(_, msg: Message):
        if current_quiz["word"] is None:
            return await msg.reply("There is no active quiz.")

        current_quiz["word"] = None
        current_quiz["hint"] = None
        current_quiz["answer_mode"] = False

        await msg.reply("🛑 **Quiz stopped successfully.**")
