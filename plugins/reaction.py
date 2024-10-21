from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, ChannelInvalid
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
from ChampuMusic.plugins.link_command_handler import link_command_handler  # Import the function
import asyncio
import random

# Replace this with your actual log group chat ID
LOG_GROUP_ID = -1001423108989

async def send_log(message: str, channel_id: int = None, message_id: int = None):
    try:
        if channel_id and message_id:
            link = await link_command_handler(channel_id, message_id)  # Use the imported function
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("ɢᴏ ᴛᴏ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ", url=link)]
            ])
            await app.send_message(LOG_GROUP_ID, message, reply_markup=button)
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
            await message.reply(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʀᴇᴀᴄᴛɪᴏɴ. ᴇʀʀᴏʀ: {str(e)}")
    else:
        await message.reply("ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴀᴄᴛ ᴛᴏ ɪᴛ.")
@app.on_message(filters.channel)
async def auto_react_to_channel_post(client, message: Message):
    try:
        # Check if the bot is a member of the channel
        try:
            chat = await client.get_chat(message.chat.id)
            await send_log(f"ᴄʜᴀᴛ ɪɴғᴏ: ɪᴅ={chat.id}, ᴛʏᴘᴇ={chat.type}, ᴛɪᴛʟᴇ={chat.title}")
            
            if chat.type not in ["channel", "supergroup"]:
                await send_log(f"ɴᴏᴛ ᴀ ᴄʜᴀɴɴᴇʟ: {message.chat.id}")
                return
        except ChannelInvalid:
            await send_log(f" ʙᴏᴛ ɪs ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ: {message.chat.id}")
            return

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
            f"ʀᴇᴀᴄᴛᴇᴅ ᴛᴏ ᴍᴇssᴀɢᴇ {message.id} ɪɴ ᴄʜᴀɴɴᴇʟ {message.chat.title}",
            channel_id=message.chat.id,
            message_id=message.id
        )
    except Exception as e:
        await send_log(
            f"ғᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴀᴄᴛ ᴛᴏ ᴄʜᴀɴɴᴇʟ ᴘᴏsᴛ. ᴇʀʀᴏʀ: {str(e)}",
            channel_id=message.chat.id,
            message_id=message.id
        )