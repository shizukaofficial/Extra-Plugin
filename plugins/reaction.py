from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
import asyncio
import random

# Replace this with your actual log group chat ID
LOG_GROUP_ID = -1001423108989

async def send_log(message: str, chat_id: int, chat_title: str, message_id: int):
    try:
        channel_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")]
        ])
        await app.send_message(
            LOG_GROUP_ID,
            f"{message}\n\nChannel: {chat_title}\nChannel ID: `{chat_id}`\nMessage ID: `{message_id}`",
            reply_markup=channel_button
        )
    except Exception as e:
        print(f"Failed to send log: {e}")

async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            retries += 1
            delay = initial_delay * (2 ** retries) + random.uniform(0, 1)
            await send_log(
                f"ғʟᴏᴏᴅᴡᴀɪᴛ ᴅᴇᴛᴇᴄᴛᴇᴅ. ʀᴇᴛʀʏɪɴɢ ɪɴ {delay:.2f} sᴇᴄᴏɴᴅs...",
                kwargs.get('chat_id', 'Unknown'),
                kwargs.get('chat_title', 'Unknown'),
                kwargs.get('message_id', 'Unknown')
            )
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
            await message.reply(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʀᴇᴀᴄᴛɪᴏɴ. ᴇʀʀᴏʀ: {str(e)}")
    else:
        await message.reply("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴀᴄᴛ ᴛᴏ ɪᴛ.")
        
@app.on_message(filters.channel)
async def auto_react_to_channel_post(client, message: Message):
    try:
        await retry_with_backoff(
            client.send_reaction,
            chat_id=message.chat.id,
            message_id=message.id,
            emoji='👍'
        )
        
        assistant = await get_assistant(message.chat.id)
        if assistant:
            await retry_with_backoff(
                assistant.send_reaction,
                chat_id=message.chat.id,
                message_id=message.id,
                emoji='❤️'
            )
        
        await send_log(
            f"ʀᴇᴀᴄᴛᴇᴅ ᴛᴏ ᴍᴇssᴀɢᴇ",
            message.chat.id,
            message.chat.title,
            message.id
        )
    except Exception as e:
        await send_log(
            f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴄᴛ ᴛᴏ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ. ᴇʀʀᴏʀ: {str(e)}",
            message.chat.id,
            message.chat.title,
            message.id
        )