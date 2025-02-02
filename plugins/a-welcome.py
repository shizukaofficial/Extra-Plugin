import random
import asyncio
import time
from logging import getLogger
from pyrogram import enums, filters, Client
from pyrogram.types import ChatMemberUpdated, Message

from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
from pymongo import MongoClient
from config import MONGO_DB_URI

LOGGER = getLogger(__name__)

champu = [
    "ʜᴇʏ", "ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ?", "ʜᴇʟʟᴏ", "ʜɪ", "ᴋᴀɪsᴇ ʜᴏ?", "ᴡᴇʟᴄᴏᴍᴇ ᴊɪ", "ᴡᴇʟᴄᴏᴍᴇ",
    "ᴀᴀɪʏᴇ ᴀᴀɪʏᴇ", "ᴋᴀʜᴀ ᴛʜᴇ ᴋᴀʙsᴇ ᴡᴀɪᴛ ᴋᴀʀ ʀʜᴇ ᴀᴘᴋᴀ", "ɪss ɢʀᴏᴜᴘ ᴍᴀɪɴ ᴀᴘᴋᴀ sᴡᴀɢᴀᴛ ʜᴀɪ",
    "ᴏʀ ʙᴀᴛᴀᴏ sᴜʙ ʙᴀᴅʜɪʏᴀ", "ᴀᴘᴋᴇ ᴀᴀɴᴇ sᴇ ɢʀᴏᴜᴘ ᴏʀ ᴀᴄʜʜᴀ ʜᴏɢʏᴀ"
]

awelcomedb = MongoClient(MONGO_DB_URI)
astatus_db = awelcomedb.awelcome_status_db.status

async def is_assistant_admin(client, chat_id):
    assistant = await get_assistant(chat_id)
    if not assistant:
        return False
    try:
        member = await client.get_chat_member(chat_id, assistant.id)
        return member.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
    except Exception:
        return False

async def get_awelcome_status(chat_id):
    status = astatus_db.find_one({"chat_id": chat_id})
    return status.get("welcome", "on") if status else "on"

async def set_awelcome_status(chat_id, state):
    astatus_db.update_one({"chat_id": chat_id}, {"$set": {"welcome": state}}, upsert=True)

@app.on_message(filters.command("awelcome") & filters.group)
async def awelcome_command(client, message: Message):
    chat_id = message.chat.id

    if not await is_assistant_admin(client, chat_id):
        await message.reply_text("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴅᴏᴇsɴ'ᴛ ᴡᴏʀᴋ ᴡɪᴛʜᴏᴜᴛ ɢɪᴠɪɴɢ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇs ᴛᴏ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ ᴏғ ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ.")
        return

    usage = "**ᴜsᴀɢᴇ:**\n**⦿ /awelcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("**sᴏʀʀʏ, ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴏɢɢʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs!**")

    state = message.text.split(None, 1)[1].strip().lower()
    current_status = await get_awelcome_status(chat_id)

    if state == "off":
        if current_status == "off":
            await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ!**")
        else:
            await set_awelcome_status(chat_id, "off")
            await message.reply_text(f"**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ɪɴ {message.chat.title}!**")

    elif state == "on":
        if current_status == "on":
            await message.reply_text("**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴀʟʀᴇᴀᴅʏ ᴇɴᴀʙʟᴇᴅ!**")
        else:
            await set_awelcome_status(chat_id, "on")
            await message.reply_text(f"**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴇɴᴀʙʟᴇᴅ ɪɴ {message.chat.title}!**")

    else:
        await message.reply_text(usage)

@app.on_chat_member_updated(filters.group, group=5)
async def greet_new_members(client: Client, member: ChatMemberUpdated):
    chat_id = member.chat.id

    if not await is_assistant_admin(client, chat_id):
        await client.send_message(chat_id, "ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴅᴏᴇsɴ'ᴛ ᴡᴏʀᴋ ᴡɪᴛʜᴏᴜᴛ ɢɪᴠɪɴɢ ᴀᴅᴍɪɴ ᴘʀɪᴠɪʟᴇɢᴇs ᴛᴏ ᴛʜᴇ ᴀssɪsᴛᴀɴᴛ ᴀᴄᴄᴏᴜɴᴛ ᴏғ ᴛʜᴇ ᴍᴜsɪᴄ ʙᴏᴛ.")
        return

    welcome_status = await get_awelcome_status(chat_id)
    if welcome_status == "off":
        return

    if member.new_chat_member and not member.old_chat_member:
        user = member.new_chat_member.user
        welcome_text = f"{user.mention}, {random.choice(champu)}"
        assistant = await get_assistant(chat_id)
        if assistant:
            await assistant.send_message(chat_id, text=welcome_text)
