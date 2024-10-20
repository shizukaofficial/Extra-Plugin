from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
import asyncio
import random

async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            retries += 1
            delay = initial_delay * (2 ** retries) + random.uniform(0, 1)
            print(f"FloodWait detected. Retrying in {delay:.2f} seconds...")
            await asyncio.sleep(delay)
    raise Exception(f"Failed after {max_retries} retries")

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
                
                await message.reply(f"Assistant reacted with {emoji} to the message!")
            else:
                await message.reply("Assistant not available for this chat.")
        except Exception as e:
            await message.reply(f"Failed to send reaction. Error: {str(e)}")
    else:
        await message.reply("Please reply to a message to react to it.")

@app.on_message(filters.channel)
async def auto_react_to_channel_post(client, message: Message):
    try:
        await retry_with_backoff(
            client.send_reaction,
            chat_id=message.chat.id,
            message_id=message.id,
            emoji='❤️'
        )
        
        assistant = await get_assistant(message.chat.id)
        if assistant:
            await retry_with_backoff(
                assistant.send_reaction,
                chat_id=message.chat.id,
                message_id=message.id,
                emoji='❤️'
            )
        
        print(f"Reacted to message {message.id} in channel {message.chat.title}")
    except Exception as e:
        print(f"Failed to react to channel post. Error: {str(e)}")