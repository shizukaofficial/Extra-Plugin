import random
import asyncio
import logging
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated
from pymongo import MongoClient
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
from config import MONGO_DB_URI

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

# Constants
OWNER_ID = 6399386263  # Replace with the actual owner ID
SPAM_THRESHOLD = 3
SPAM_WINDOW_SECONDS = 5

# Database setup
db_client = MongoClient(MONGO_DB_URI)
group_db = db_client.telegram_bot.approved_groups

# In-memory tracking for spam protection
user_last_message_time = {}
user_command_count = {}

# Response messages
RESPONSES = [
    "Hii! Kaise ho? 😊",
    "Main thik hoon, tum kaise ho? 🌸",
    "Wow, yeh toh amazing hai! 😍",
    "Acha yeh batao, aur kya chal raha hai? 🧐",
    "Tumhare baare mein aur jaan ne ka mann kar raha hai! 🥰",
    "Sach mein, mazaa aa gaya! ❤️",
    "Aapki baatein hamesha achhi lagti hain! 🥀",
    "Mujhe yeh pasand aaya! 🤗"
]

# Helper Functions
async def is_group_approved(chat_id):
    """Check if a group is approved."""
    group = group_db.find_one({"chat_id": chat_id})
    return bool(group)

async def set_group_approval(chat_id, state):
    """Set the approval status of a group."""
    if state:
        group_db.update_one({"chat_id": chat_id}, {"$set": {"approved": True}}, upsert=True)
    else:
        group_db.delete_one({"chat_id": chat_id})

# Command to approve/disapprove groups
@app.on_message(filters.command("approvegroup") & ~filters.private)
async def approve_group(_, message):
    """Approve or disapprove a group."""
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Only the owner can manage group approvals!")

    if len(message.command) != 2:
        return await message.reply("⚙️ Usage: `/approvegroup [on|off]`")

    state = message.command[1].lower()
    if state not in ["on", "off"]:
        return await message.reply("❌ Invalid state! Use 'on' or 'off'.")

    chat_id = message.chat.id
    if state == "on":
        await set_group_approval(chat_id, True)
        await message.reply(f"✅ Group `{message.chat.title}` approved for bot interaction!")
    else:
        await set_group_approval(chat_id, False)
        await message.reply(f"🚫 Group `{message.chat.title}` disapproved!")

# Respond to text messages
@app.on_message(filters.text & ~filters.private)
async def reply_to_messages(_, message):
    """Reply to messages in approved groups."""
    chat_id = message.chat.id

    if not await is_group_approved(chat_id):
        return

    if message.from_user and message.from_user.is_self:
        return

    user_id = message.from_user.id
    current_time = asyncio.get_event_loop().time()

    # Spam protection
    last_message_time = user_last_message_time.get(user_id, 0)
    if current_time - last_message_time < SPAM_WINDOW_SECONDS:
        user_command_count[user_id] = user_command_count.get(user_id, 0) + 1
        if user_command_count[user_id] > SPAM_THRESHOLD:
            try:
                await message.reply("⚠️ Please avoid spamming. Try again after a while.")
            except Exception as e:
                LOGGER.error(f"Failed to send spam warning: {e}")
            return
    else:
        user_command_count[user_id] = 1

    user_last_message_time[user_id] = current_time

    # Respond with a random message
    response = random.choice(RESPONSES)
    try:
        await asyncio.sleep(2)  # Simulate a natural delay
        userbot = await get_assistant(chat_id)
        await userbot.send_message(chat_id, response)
        LOGGER.info(f"Replied to {user_id} with: {response}")
    except Exception as e:
        LOGGER.error(f"Error in replying: {e}")

# Greet new members
@app.on_chat_member_updated(filters.group, group=5)
async def greet_new_members(_, member: ChatMemberUpdated):
    """Greet new members in approved groups."""
    try:
        chat_id = member.chat.id
        if not await is_group_approved(chat_id):
            return

        userbot = await get_assistant(chat_id)  # Using the assistant bot for sending messages
        user = member.new_chat_member.user

        if member.new_chat_member and not member.old_chat_member:
            welcome_text = f"Welcome {user.mention}! 🎉"
            await userbot.send_message(chat_id, text=welcome_text)

    except Exception as e:
        LOGGER.error(f"Error greeting new members: {e}")

# Command to check bot status
@app.on_message(filters.command("status") & ~filters.private)
async def check_status(_, message):
    """Check the bot's status."""
    chat_id = message.chat.id
    if not await is_group_approved(chat_id):
        return await message.reply("❌ This group is not approved!")

    await message.reply("👋 The assistant is active and running smoothly!")

# Command to stop the assistant
@app.on_message(filters.command("astop") & ~filters.private)
async def stop_assistant(_, message):
    """Stop the assistant in the current group."""
    if message.from_user.id != OWNER_ID:
        return await message.reply("❌ Only the owner can stop the assistant!")

    await message.reply("🚫 Assistant is shutting down!")
    await app.stop()
