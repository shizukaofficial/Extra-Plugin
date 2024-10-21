from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
from ChampuMusic.plugins.tools.invitelink import get_invite_link
import asyncio
import random

# Replace this with your actual log group chat ID
LOG_GROUP_ID = -1001423108989

async def send_log(message: str, chat_id: int = None, chat_title: str = None):
    try:
        if chat_id and chat_title:
            invite_link = await get_invite_link(chat_id)
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("Channel Link", url=invite_link)]])
            await app.send_message(LOG_GROUP_ID, message, reply_markup=keyboard)
        else:
            await app.send_message(LOG_GROUP_ID, message)
    except Exception as e:
        print(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʟᴏɢ ᴍᴇssᴀɢᴇ: {str(e)}")

async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            retries += 1
            delay = initial_delay * (2 ** retries) + random.uniform(0, 1)
            await send_log(f"ғʟᴏᴏᴅᴡᴀɪᴛ ᴅᴇᴛᴇᴄᴛᴇᴅ. ʀᴇᴛʀʏɪɴɢ ɪɴ {delay:.2f} sᴇᴄᴏɴᴅs...")
            await asyncio.sleep(delay)
    raise Exception(f"ғᴀɪʟᴇᴅ ᴀғᴛᴇʀ {max_retries} ʀᴇᴛʀɪᴇs")

@app.on_message(filters.command("react"))
async def react_to_message(client, message: Message):
    if message.reply_to_message:
        try:
            emoji = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else '👍'
            
            assistant = await get_assistant(message.chat.id)
            if assistant:
                await retry_with_backoff(
                    assistant.send_reaction,
                    chat_id=message.chat.id,
                    message_id=message.reply_to_message.id,
                    emoji=emoji
                )
            else:
                await message.reply("ᴀssɪsᴛᴀɴᴛ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ʜᴇʀᴇ ғᴏʀ ʀᴇᴀᴄᴛ ᴏɴ ᴍᴇssᴀɢᴇ.")
        except Exception as e:
            await message.reply(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʀᴇᴀᴄᴛɪᴏɴ. ᴇʀʀ ᴏʀ: {str(e)}")
    else:
        await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴀᴄᴛ.")

@app.on_message(filters.new_chat_members)
async def new_member(client, message: Message):
    if message.new_chat_members:
        for member in message.new_chat_members:
            if member.id == client.me.id:
                assistant = await get_assistant(message.chat.id)
                if assistant:
                    await retry_with_backoff(assistant.join_chat, message.chat.id)
                else:
                    await message.reply("ᴀssɪsᴛᴀɴᴛ ɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ ʜᴇʀᴇ ғᴏʀ ᴊᴏɪɴɪɴɢ ᴄʜᴀᴛ.")