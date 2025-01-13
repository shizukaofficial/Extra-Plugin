import random
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from ChampuMusic import app


# Approved group and owner configuration
APPROVED_GROUP_IDS = [-1001961655253]  # Replace with your approved group ID(s)
OWNER_ID = 6399386263  # Replace with your Telegram user ID

# Sample responses for the bot
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

# Path to save the session file (using a shorter path)
SESSION_FILE_PATH = "/data/user/0/ru.iiec.pydroid3/files/userbot_session.session"

# Function to reply to messages
@app.on_message(filters.text)
async def reply_to_messages(client, message):
    # Ensure the bot replies only in approved groups
    if message.chat.id not in APPROVED_GROUP_IDS:
        return

    # Ignore messages sent by the bot itself
    if message.from_user.is_bot:
        return

    # Generate a random response
    response = random.choice(RESPONSES)

    try:
        # Add a delay to avoid hitting Telegram rate limits
        await asyncio.sleep(2)
        await message.reply(response)
        print(f"Replied to {message.from_user.id} with: {response}")
    except FloodWait as e:
        print(f"Flood wait error: Must wait {e.x} seconds before sending more messages.")
        await asyncio.sleep(e.x)  # Wait for the penalty duration
    except Exception as e:
        print(f"Failed to reply: {e}")


# Command to check bot status (owner only)
@app.on_message(filters.command("astatus"))
async def check_status(client, message):
    if message.chat.id not in APPROVED_GROUP_IDS or message.from_user.id != OWNER_ID:
        return

    await message.reply("👋 Userbot is active and running smoothly!")


# Command to stop the bot (owner only)
@app.on_message(filters.command("astop"))
async def stop_bot(client, message):
    if message.chat.id not in APPROVED_GROUP_IDS or message.from_user.id != OWNER_ID:
        return

    await message.reply("🚫 Userbot is shutting down!")
    await app.stop()

