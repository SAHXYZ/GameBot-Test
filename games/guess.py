# filename: games/guess.py

from pyrogram import Client, filters
from pyrogram.types import Message

# ✅ Use MongoDB
from database.mongo import get_user, update_user

import random

# Active games (in-memory)
active_games = {}

# Dictionary of hints
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
    "island": "Land completely surrounded by water.",
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
    "orange": "A citrus fruit known for its vitamin C.",
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
    "notebook": "A small book of blank pages for writing.",
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
    "castle": "A large fortified building from ancient times.",
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
    "leader": "Someone who guides or commands others.",
    "king": "A male ruler of a kingdom.",
    "queen": "A female ruler of a kingdom.",
    "prince": "A male royal family member.",
    "princess": "A female royal family member.",
    "monkey": "A playful animal that climbs trees.",
    "tiger": "A large striped wild cat.",
    "lion": "A powerful big cat known as the king of the jungle.",
    "horse": "An animal often used for riding.",
    "rabbit": "A small animal with long ears.",
    "mouse": "A tiny rodent attracted to food.",
    "eagle": "A bird known for sharp eyesight.",
    "parrot": "A bird that can mimic human speech.",
    "pigeon": "A common city bird.",
    "spider": "An insect-like creature with eight legs.",
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
    "stairs": "A set of steps used for climbing up and down.",
    "escalator": "Moving stairs found in malls and stations.",
    "kitchen": "A room where food is prepared.",
    "bedroom": "A room where people sleep.",
    "bathroom": "A room with toilet and shower.",
    "garden": "An outdoor area where plants grow.",
    "garage": "A place to park vehicles.",
    "factory": "A building where products are manufactured.",
    "library": "A place full of books for reading.",
    "station": "A place where trains or buses stop.",
    "airport": "A place where airplanes take off and land.",
    "stadium": "A venue for sports and events.",
    "theater": "A place for watching movies or performances.",
    "cookie": "A small sweet baked treat.",
    "butter": "A dairy product used for cooking and spreading.",
    "cheese": "A dairy food made from milk curds.",
    "honey": "A sweet sticky substance made by bees.",
    "sugar": "A sweet substance used in food and drinks.",
    "salt": "A mineral used to season food.",
    "pepper": "A spice used to flavor dishes.",
    "chicken": "A common type of poultry meat.",
    "pizza": "A dish made with dough, sauce, cheese, and toppings.",
    "burger": "A sandwich with a patty between buns.",
    "noodle": "Long, thin pieces of dough eaten with sauces.",
    "pasta": "Italian noodles made from wheat flour.",
    "salad": "A dish of mixed vegetables.",
    "soup": "A liquid dish often served warm.",
    "steak": "A thick cut of beef.",
    "bacon": "Salt-cured meat usually served crispy.",
    "coffee": "A hot drink made from roasted beans.",
    "tea": "A beverage made by steeping leaves in hot water.",
    "juice": "Liquid extracted from fruits.",
    "milk": "A white liquid produced by mammals.",
    "chocolate": "A sweet made from cocoa beans.",
    "cereal": "Grains eaten for breakfast.",
    "avocado": "A creamy fruit used for guacamole.",
    "carrot": "An orange root vegetable.",
    "tomato": "A red fruit often used in salads.",
    "potato": "A starchy vegetable used in many dishes.",
    "onion": "A vegetable known for its strong smell.",
    "peppermint": "A cool-flavored herb used in candies.",
    "ginger": "A spicy root used in cooking and tea.",
    "garlic": "A strong-smelling bulb used in cooking.",
    "cucumber": "A long green vegetable with high water content.",
    "pumpkin": "A large orange vegetable used in pies.",
    "coconut": "A tropical fruit with hard shell and white flesh.",
    "dragon": "A mythical creature that breathes fire.",
    "wizard": "Someone who uses magic spells.",
    "witch": "A person believed to use magical powers.",
    "ghost": "A spirit of a dead person.",
    "zombie": "A reanimated corpse from horror stories.",
    "robot": "A machine capable of performing tasks.",
    "alien": "A creature from another planet.",
    "giant": "A creature much larger than humans.",
    "knight": "A medieval warrior with armor.",
    "archer": "A person skilled in using a bow and arrow.",
    "villain": "The antagonist or bad character in a story.",
    "hero": "The main character who saves the day.",
    "portal": "A doorway to another world.",
    "crystal": "A transparent mineral with geometric shapes.",
    "treasure": "A collection of valuable items."
}

WORD_LIST = list(HINTS.keys())


def init_guess(bot: Client):

    # -------------------------
    # START GAME
    # -------------------------
    @bot.on_message(filters.command("guess"))
    async def start_guess(_, msg: Message):
        if not msg.from_user:
            return

        user_id = str(msg.from_user.id)

        if user_id in active_games:
            return await msg.reply("You already have an active game.\nUse /stop to end it.")

        # Pick random word
        word = random.choice(WORD_LIST)
        hint = HINTS[word]

        active_games[user_id] = {
            "word": word,
            "hint": hint,
            "answer_mode": False,
        }

        await msg.reply(
            f"🧩 **Guess The Word!**\n\n"
            f"🔎 **Hint:** {hint}\n\n"
            f"Type **/answer** to enter guessing mode."
        )

    # -------------------------
    # ENABLE ANSWER MODE
    # -------------------------
    @bot.on_message(filters.command("answer"))
    async def enable_answer_mode(_, msg: Message):

        user_id = str(msg.from_user.id)

        if user_id not in active_games:
            return await msg.reply("No active game.\nUse /guess to start.")

        active_games[user_id]["answer_mode"] = True

        await msg.reply(
            "📝 **Answer mode ON!**\n"
            "Send your guesses normally.\n"
            "Use /stop to end the game."
        )

    # -------------------------
    # PROCESS GUESSES
    # -------------------------
    @bot.on_message(filters.text & ~filters.command(["guess", "answer", "stop"]))
    async def check_guess(_, msg: Message):

        user_id = str(msg.from_user.id)

        if user_id not in active_games:
            return

        # Must be in answer mode
        if not active_games[user_id]["answer_mode"]:
            return

        guess = msg.text.strip().lower()
        correct = active_games[user_id]["word"]

        if guess == correct:

            # Reward user in BRONZE (MongoDB)
            user = get_user(msg.from_user.id)
            reward = random.randint(20, 120)

            new_bronze = user.get("bronze", 0) + reward

            update_user(msg.from_user.id, {"bronze": new_bronze})

            del active_games[user_id]

            return await msg.reply(
                f"🎉 **Correct!**\n"
                f"You earned **{reward} Bronze 🥉**!"
            )

        await msg.reply("❌ Wrong guess. Try again!")

    # -------------------------
    # STOP GAME
    # -------------------------
    @bot.on_message(filters.command("stop"))
    async def stop_guess(_, msg: Message):

        user_id = str(msg.from_user.id)

        if user_id in active_games:
            del active_games[user_id]
            return await msg.reply("🛑 Guess game stopped.")

        await msg.reply("You have no active game.")
