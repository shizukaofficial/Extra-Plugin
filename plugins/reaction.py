from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from ChampuMusic import app
from config import LOGGER_ID
from ChampuMusic.utils.database import get_assistant
import asyncio
import random

# Example static list of possible reactions (this should ideally be dynamic)
DEFAULT_REACTION_LIST = ['👍', '❤️', '😂', '😮', '😢', '🔥', '🎉']

async def send_log(message: str, chat_id: int, chat_title: str, message_id: int):
    try:
        channel_button = InlineKeyboardMarkup([
            [InlineKeyboardButton(text="Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")]
        ])
        await app.send_message(
            LOGGER_ID,
            f"{message}\n\nChannel: {chat_title}\nChannel ID: `{chat_id}`\nMessage ID: `{message_id}`",
            reply_markup=channel_button
        )
    except Exception as e:
        print(f"Failed to send log: {e}")

async def get_channel_reactions(chat_id):
    # This function should return the allowed reactions for the given channel
    # For now, we'll just return the default list, but in a real scenario,
    # you would implement logic to fetch the actual allowed reactions.
    return DEFAULT_REACTION_LIST

async def retry_with_backoff(func, *args, max_retries=5, initial_delay=1, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            retries += 1
            delay = initial_delay * (2 ** retries) + random.uniform(0, 1)
            await send_log(
                f"FloodWait detected. Retrying in {delay:.2f} seconds...",
                kwargs.get('chat_id', 'Unknown'),
                kwargs.get('chat_title', 'Unknown'),
                kwargs.get('message_id', 'Unknown')
            )
            await asyncio.sleep(delay)
    raise Exception(f"Failed after {max_retries} retries")

@app.on_message(filters.command("react"))
async def react_to_message(client, message: Message):
    if message.reply_to_message:
        try:
            allowed_reactions = await get_channel_reactions(message.chat.id)
        
            if not allowed_reactions:
                await message.chat.send_message(
                    f"No reactions available for in this group.",
                    message.chat.id,
                    message.chat.title,
                    message.id
                )
                return
            assistant = await get_assistant(message.chat.id)
            if assistant:
                bot_group_react = random.choice(allowed_reactions)
                # React with the assistant's emoji
                await retry_with_backoff(
                    assistant.send_reaction,
                    chat_id=message.chat.id,
                    message_id=message.reply_to_message.id,
                    emoji=bot_group_react
                )
            else:
                await message.reply("Assistant not available here for react on message.")
            assistant_group_react = random.choice(allowed_reactions)
            # React with the bot's emoji
            await retry_with_backoff(
                client.send_reaction,
                chat_id=message.chat.id,
                message_id=message.reply_to_message.id,
                emoji=assistant_group_react
            )
        
        except Exception as e:
            await message.reply(f"Failed to send reaction. Error: {str(e)}")
    else:
        await message.reply("Please reply to a message to react to it.")

@app.on_message(filters.channel)
async def auto_react_to_channel_post(client, message: Message):
    try:
        # Get the allowed reactions for the channel
        allowed_reactions = await get_channel_reactions(message.chat.id)
        
        if not allowed_reactions:
            await send_log(
                f"No reactions available for this channel.",
                message.chat.id,
                message.chat.title,
                message.id
            )
            return
        
        # Randomly select a reaction from the allowed reactions
        selected_reaction = random.choice(allowed_reactions)
        
        await retry_with_backoff(
            client.send_reaction,
            chat_id=message.chat.id,
            message_id=message.id,
            emoji=selected_reaction
        )
        
        assistant = await get_assistant(message.chat.id)
        if assistant:
            # Randomly select a reaction for the assistant as well
            assistant_reaction = random.choice(allowed_reactions)
            await retry_with_backoff(
                assistant.send_reaction,
                chat_id=message.chat.id,
                message_id=message.id,
                emoji=assistant_reaction
            )
        
        await send_log(
            f"Reacted to message with {selected_reaction}",
            message.chat.id,
            message.chat.title,
            message.id
        )
    except Exception as e:
        await send_log(
            f"Failed to react to channel post. Error: {str(e)}",
            message.chat.id,
            message.chat.title,
            message.id
        )