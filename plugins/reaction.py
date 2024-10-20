from pyrogram import Client, filters
from pyrogram.types import Message
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant

@app.on_message(filters.command("react"))
async def react_to_message(client, message: Message):
    if message.reply_to_message:
        try:
            emoji = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else '❤️'
            
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
            
        except Exception as e:
            print(f"ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ ʀᴇᴀᴄᴛɪᴏɴ. ᴇʀʀᴏʀ: {str(e)}")
    else:
        print("No message was replied to.")

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
        
        print(f"Reacted to message {message.id} in group {message.chat.title}")
    except Exception as e:
        print(f"Failed to react to group message. Error: {str(e)}")