from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait  # Import FloodWait
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
import asyncio  # Import asyncio to handle sleeping during FloodWait

# Replace this with your actual log group ID
LOG_GROUP_ID = -1001423108989

async def send_to_log_group(message: str):
    try:
        await app.send_message(LOG_GROUP_ID, message)
    except Exception as e:
        print(f"Failed to send message to log group: {str(e)}")

@app.on_message(filters.command("react"))
async def react_to_message(client, message: Message):
    if message.reply_to_message:
        try:
            emoji = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else '👍'
            
            # Bot reaction
            await client.send_reaction(
                chat_id=message.chat.id,
                message_id=message.reply_to_message.id,
                emoji='👀'  # Bot's reaction
            )
            
            # Get the assistant client
            assistant = await get_assistant(message.chat.id)
            if assistant:
                # Make the assistant react to the replied message
                await assistant.send_reaction(
                    chat_id=message.chat.id,
                    message_id=message.reply_to_message.id,
                    emoji=emoji  # User-specified or default emoji
                )
            
            await send_to_log_group(f"Reacted to message {message.reply_to_message.id} in group {message.chat.title}")
        except FloodWait as e:
            # Handle the FloodWait by sleeping for the specified duration
            print(f"FloodWait encountered. Sleeping for {e.value} seconds.")
            await asyncio.sleep(e.value)
            await send_to_log_group(f"FloodWait occurred while reacting to message {message.reply_to_message.id}. Retrying after {e.value} seconds.")
            await react_to_message(client, message)  # Retry the function after waiting
        except Exception as e:
            await send_to_log_group(f"Failed to send reaction in group {message.chat.title}. Error: {str(e)}")
    else:
        await send_to_log_group("No message was replied to for reaction command.")

@app.on_message(filters.command(["reacton", "reactionon"]) & filters.group)
async def turn_on_reactions(client, message: Message):
    await message.reply_text("Reactions have been enabled in this group.")
    await send_to_log_group(f"Reactions enabled in group {message.chat.title}")

@app.on_message(filters.command(["reactoff", "reactionoff"]) & filters.group)
async def turn_off_reactions(client, message: Message):
    await message.reply_text("Reactions have been disabled in this group.")
    await send_to_log_group(f"Reactions disabled in group {message.chat.title}")

@app.on_message(filters.group)
async def auto_react_to_group_message(client, message: Message):
    try:
        # Bot reaction
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji='👀'  # You can change this to any emoji you prefer for the bot
        )
        
        # Get the assistant client
        assistant = await get_assistant(message.chat.id)
        if assistant:
            await assistant.send_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                emoji='❤️'  # You can change this to any emoji you prefer for the assistant
            )
        
        await send_to_log_group(f"Reacted to message {message.id} in group {message.chat.title}")
    except FloodWait as e:
        # Handle the FloodWait by sleeping for the specified duration
        print(f"FloodWait encountered. Sleeping for {e.value} seconds.")
        await asyncio.sleep(e.value)
        await send_to_log_group(f"FloodWait occurred while auto-reacting in group {message.chat.title}. Retrying after {e.value} seconds.")
        await auto_react_to_group_message(client, message)  # Retry the function after waiting
    except Exception as e:
        await send_to_log_group(f"Failed to react to group message in {message.chat.title}. Error: {str(e)}")
