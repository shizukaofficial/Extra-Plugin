from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from ChampuMusic import app
from config import LOGGER_ID
from ChampuMusic.utils.database import get_assistant
import asyncio
import random

DEFAULT_REACTION_LIST = ['👍', '❤️', '😂', '😮', '😢', '🔥', '🎉']

async def send_log(message: str, chat_id: int, chat_title: str, message_id: int):
    try:
        channel_button = InlineKeyboardMarkup([[
            InlineKeyboardButton(text="Go to Message", url=f"https://t.me/c/{str(chat_id)[4:]}/{message_id}")
        ]])
        await app.send_message(
            LOGGER_ID,
            f"{message}\n\nChannel: {chat_title}\nChannel ID: `{chat_id}`\nMessage ID: `{message_id}`",
            reply_markup=channel_button
        )
    except Exception as e:
        print(f"Failed to send log: {e}")

async def get_channel_reactions(chat_id):
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
        except Exception as e:
            # Log the error and return None to indicate failure
            print(f"Error in retry_with_backoff: {str(e)}")
            return None
    raise Exception(f"Failed after {max_retries} retries")

async def send_reaction_with_fallback(client, chat_id, message_id, emoji, max_retries=3):
    for _ in range(max_retries):
        try:
            await client.send_reaction(chat_id=chat_id, message_id=message_id, emoji=emoji)
            return  # Success, exit the function
        except Exception as e:
            print(f"Failed to send reaction {emoji}: {str(e)}")
            # Select a new random emoji
            emoji = random.choice(DEFAULT_REACTION_LIST)
    raise Exception(f"Failed to send reaction after {max_retries} attempts")

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
                print(f"Selected reaction for assistant: {bot_group_react}")
                await send_reaction_with_fallback(
                    assistant,
                    message.chat.id,
                    message.reply_to_message.id,
                    bot_group_react
                )
            else:
                await message.reply("Assistant not available here for react on message.")
                
            assistant_group_react = random.choice(allowed_reactions)
            print(f"Selected reaction for client: {assistant_group_react}")
            await send_reaction_with_fallback(
                client,
                message.chat.id,
                message.reply_to_message.id,
                assistant_group_react
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