import random
import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

APPROVED_GROUP_IDS = [-1001961655253]
OWNER_ID = 6399386263 

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


@Client.on_message(filters.text)
async def reply_to_messages(client, message):
    if message.chat.id not in APPROVED_GROUP_IDS:
        return
    if message.from_user and message.from_user.is_self:
        return

    response = random.choice(RESPONSES)

    try:
        await asyncio.sleep(2)
        await message.reply(response)
        print(f"Replied to {message.from_user.id} with: {response}")
    except FloodWait as e:
        print(f"Flood wait error: Must wait {e.x} seconds before sending more messages.")
        await asyncio.sleep(e.x) 
    except Exception as e:
        print(f"Failed to reply: {e}")


@Client.on_message(filters.command(["status"], prefixes=["."]))
async def check_status(client, message):
    if message.chat.id not in APPROVED_GROUP_IDS or message.from_user.id != OWNER_ID:
        return

    await message.reply("👋 Assistant is active and running smoothly!")


@Client.on_message(filters.command("astop", prefixes=["."]))
async def stop_assistant(client, message):
    if message.chat.id not in APPROVED_GROUP_IDS or message.from_user.id != OWNER_ID:
        return

    await message.reply("🚫 Assistant is shutting down!")
    await assistant.stop()
