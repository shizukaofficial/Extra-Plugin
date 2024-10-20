from pyrogram import Client, filters
from pyrogram.types import Message
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant

@app.on_message(filters.command("react"))
async def react_to_message(client, message: Message):
    if message.reply_to_message:
        try:
            emoji = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else '👍'
            
            # Get the assistant client
            assistant = await get_assistant(message.chat.id)
            if assistant:
                # Make the assistant react to the replied message
                await assistant.send_reaction(
                    chat_id=message.chat.id,
                    message_id=message.reply_to_message.id,
                    emoji=emoji  # Note the lowercase 'emoji'
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
        # Send a reaction to the new message
        await client.send_reaction(
            chat_id=message.chat.id,
            message_id=message.id,
            emoji='❤️'  # You can change this to any emoji you prefer
        )
        
        # Get the assistant client
        assistant = await get_assistant(message.chat.id)
        if assistant:
            await assistant.send_reaction(
                chat_id=message.chat.id,
                message_id=message.id,
                emoji='❤️'  # Note the lowercase 'emoji'
            )
        
        print(f"Reacted to message {message.id} in channel {message.chat.title}")
    except Exception as e:
        print(f"Failed to react to channel post. Error: {str(e)}")