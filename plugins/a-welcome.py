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

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@app.on_message(filters.command("awelcome") & filters.group)
async def awelcome_command(client, message: Message):
    chat_id = message.chat.id

    assistant = await get_assistant(chat_id)
    if not assistant:
        return await message.reply_text("⚠️ **Assistant account not found. Please try again later.**")

    # Check if assistant is in the group
    try:
        member = await client.get_chat_member(chat_id, assistant.id)
        is_in_group = True
    except:
        is_in_group = False

    if not is_in_group:
        button = InlineKeyboardMarkup(
            [[InlineKeyboardButton("➕ Add Assistant", url=f"t.me/{assistant.username}?startgroup=true")]]
        )
        return await message.reply_text(
            f"⚠ **Assistant account [{assistant.username}](t.me/{assistant.username}) is not in this group.**\n"
            "➜ Please add the assistant to enable welcome messages.",
            reply_markup=button
        )

    # Check if assistant is admin
    if not await is_assistant_admin(client, chat_id):
        assistant_mention = f"@{assistant.username}" if assistant.username else f"`{assistant.id}`"
        return await message.reply_text(
            f"⚠ **This command doesn't work without giving admin privileges to {assistant_mention},** "
            "which is the assistant account of the music bot."
        )

    usage = "**Usage:**\n**⦿ /awelcome [on|off]**"
    if len(message.command) == 1:
        return await message.reply_text(usage)

    user = await app.get_chat_member(chat_id, message.from_user.id)
    if user.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
        return await message.reply_text("⚠ **Only admins can enable assistant welcome messages!**")

    state = message.text.split(None, 1)[1].strip().lower()
    current_status = await get_awelcome_status(chat_id)

    if state == "off":
        if current_status == "off":
            await message.reply_text("✅ **Welcome messages are already disabled!**")
        else:
            await set_awelcome_status(chat_id, "off")
            await message.reply_text(f"❌ **Disabled welcome messages in {message.chat.title}!**")

    elif state == "on":
        if current_status == "on":
            await message.reply_text("✅ **Welcome messages are already enabled!**")
        else:
            await set_awelcome_status(chat_id, "on")
            await message.reply_text(f"✅ **Enabled welcome messages in {message.chat.title}!**")

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
