import random
import requests
import json
from pymongo import MongoClient
from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, Message, InlineKeyboardButton, CallbackQuery
from config import MONGO_DB_URI, OWNER_ID

# Gemini API endpoint
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# Multiple Gemini API keys
GEMINI_API_KEYS = ["AIzaSyA3y2Ibkn8h9XRJlTp3YZLoWeCHge35OfM", "AIzaSyDHz1hcdMrKjuPV81IlYJ7-JLbxq6ZhJUQ"]  # Add more keys if needed

# MongoDB setup
mongo_client = MongoClient(MONGO_DB_URI)
db = mongo_client["ChampuDB"]
chats_collection = db["Champu"]  # Stores enabled chat IDs

# Global caches
reply_cache = {}  # Cache for text replies
sticker_cache = {}  # Cache for stickers
api_cache = {}  # Cache for API responses
LOAD = False  # Flag to indicate if caches are loaded

# Admin check decorator
def is_admin(func):
    async def wrapper(client, message):
        if message.from_user.id == OWNER_ID:
            return await func(client, message)
        admin = await client.get_chat_member(message.chat.id, message.from_user.id)
        if admin.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            return await func(client, message)
        await message.reply("You are not an admin!")
    return wrapper

# Load caches from MongoDB
async def load_caches():
    global reply_cache, sticker_cache, api_cache, LOAD
    if not LOAD:
        print("Loading caches from MongoDB...")
        chatdb = MongoClient(MONGO_DB_URI)
        chatai = chatdb["Word"]["WordDb"]

        # Load text replies
        for doc in chatai.find({"check": "none"}):
            reply_cache[doc["word"]] = doc["text"]

        # Load stickers
        for doc in chatai.find({"check": "sticker"}):
            sticker_cache[doc["word"]] = doc["text"]

        LOAD = True
        print("Caches loaded successfully!")

# Callback query handler
@app.on_callback_query()
async def cb_handler(_, query: CallbackQuery):
    user_id = query.from_user.id
    chat_id = query.message.chat.id
    admin = await query.message.chat.get_member(user_id)
    
    if admin.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
        return await query.answer("You're not an admin!", show_alert=True)
    
    if query.data == "addchat":
        if chats_collection.find_one({"chat_id": chat_id}):
            await query.edit_message_text("Chatbot is already enabled.")
        else:
            chats_collection.insert_one({"chat_id": chat_id})
            await query.edit_message_text(f"Chatbot enabled by {query.from_user.mention}.")
    
    elif query.data == "rmchat":
        if not chats_collection.find_one({"chat_id": chat_id}):
            await query.edit_message_text("Chatbot is already disabled.")
        else:
            chats_collection.delete_one({"chat_id": chat_id})
            await query.edit_message_text(f"Chatbot disabled by {query.from_user.mention}.")

# Command to enable/disable chatbot
@app.on_message(filters.command("chatb") & filters.group)
@is_admin
async def chaton_(client: Client, message: Message):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Disable", callback_data="rmchat")],
        [InlineKeyboardButton("Enable", callback_data="addchat")]
    ])
    await message.reply_text(
        f"Chat: {message.chat.title}\nChoose an option to enable/disable chatbot:",
        reply_markup=keyboard
    )

# Generate Hinglish response using Gemini API
async def generate_hinglish_response(prompt, user_name):
    # Check API cache first
    if prompt in api_cache:
        return api_cache[prompt]

    for api_key in GEMINI_API_KEYS:
        try:
            headers = {
                "Content-Type": "application/json"
            }
            data = {
                "contents": [
                    {
                        "parts": [
                            {"text": f"{prompt} (Respond in Hinglish and address the user as {user_name})"}
                        ]
                    }
                ]
            }
            response = requests.post(
                f"{GEMINI_API_URL}?key={api_key}",
                headers=headers,
                data=json.dumps(data)
            )
            if response.status_code == 200:
                response_data = response.json()
                if "candidates" in response_data and response_data["candidates"]:
                    response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
                    api_cache[prompt] = response_text  # Cache the response
                    return response_text
        except Exception as e:
            print(f"Gemini API Error with key {api_key}: {e}")
            continue  # Try the next API key if this one fails

    # Fallback to database if all APIs fail
    return None

@app.on_message(
    (filters.text | filters.sticker | filters.group) & ~filters.private & ~filters.bot, group=4
)
async def chatbot_text(client: Client, message: Message):
    try:
        if (
            message.text.startswith("!")
            or message.text.startswith("/")
            or message.text.startswith("?")
            or message.text.startswith("@")
            or message.text.startswith("#")
        ):
            return
    except Exception:
        pass

    # Load caches if not already loaded
    if not LOAD:
        await load_caches()

    if not message.reply_to_message:
        Champudb = MongoClient(MONGO_DB_URI)
        Champu = Champudb["ChampuDB"]["Champu"]
        is_Champu = Champu.find_one({"chat_id": message.chat.id})
        if not is_Champu:
            await client.send_chat_action(message.chat.id, ChatAction.TYPING)
            user_name = message.from_user.first_name
            response = await generate_hinglish_response(message.text, user_name)
            if response:
                await message.reply_text(response)
            else:
                # Check reply cache
                if message.text in reply_cache:
                    await message.reply_text(reply_cache[message.text])
                else:
                    K = []
                    is_chat = chatai.find({"word": message.text})
                    k = chatai.find_one({"word": message.text})
                    if k:
                        for x in is_chat:
                            K.append(x["text"])
                        hey = random.choice(K)
                        is_text = chatai.find_one({"text": hey})
                        Yo = is_text["check"]
                        if Yo == "sticker":
                            await message.reply_sticker(f"{hey}")
                        if not Yo == "sticker":
                            await message.reply_text(f"{hey}")

    if message.reply_to_message:
        Champudb = MongoClient(MONGO_DB_URI)
        Champu = Champudb["ChampuDB"]["Champu"]
        is_Champu = Champu.find_one({"chat_id": message.chat.id})
        if message.reply_to_message.from_user.id == client.id:
            if not is_Champu:
                await client.send_chat_action(message.chat.id, ChatAction.TYPING)
                user_name = message.from_user.first_name
                response = await generate_hinglish_response(message.text, user_name)
                if response:
                    await message.reply_text(response)
                else:
                    # Check reply cache
                    if message.text in reply_cache:
                        await message.reply_text(reply_cache[message.text])
                    else:
                        K = []
                        is_chat = chatai.find({"word": message.text})
                        k = chatai.find_one({"word": message.text})
                        if k:
                            for x in is_chat:
                                K.append(x["text"])
                            hey = random.choice(K)
                            is_text = chatai.find_one({"text": hey})
                            Yo = is_text["check"]
                            if Yo == "sticker":
                                await message.reply_sticker(f"{hey}")
                            if not Yo == "sticker":
                                await message.reply_text(f"{hey}")
        if not message.reply_to_message.from_user.id == client.id:
            if message.sticker:
                is_chat = chatai.find_one(
                    {
                        "word": message.reply_to_message.text,
                        "id": message.sticker.file_unique_id,
                    }
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id,
                        }
                    )
            if message.text:
                is_chat = chatai.find_one(
                    {"word": message.reply_to_message.text, "text": message.text}
                )
                if not is_chat:
                    chatai.insert_one(
                        {
                            "word": message.reply_to_message.text,
                            "text": message.text,
                            "check": "none",
                        }
                    )