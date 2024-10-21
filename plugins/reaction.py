from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, ChannelInvalid
from ChampuMusic import app
from ChampuMusic.utils.database import get_assistant
import asyncio
import random
import os
from ChampuMusic.misc import SUDOERS

# Command handler for /givelink command
@app.on_message(filters.command("givelink"))
async def give_link_command(client, message):
    # Generate an invite link for the chat where the command is used
    chat = message.chat.id
    link = await app.export_chat_invite_link(chat)
    await message.reply_text(f"Here's the invite link for this chat:\n{link}")


@app.on_message(
    filters.command(
        ["link", "invitelink"], prefixes=["/", "!", "%", ",", "", ".", "@", "#"]
    )
    & SUDOERS
)
async def link_command_handler(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply("Invalid usage. Correct format: /link group_id")
        return

    group_id = message.command[1]
    file_name = f"group_info_{group_id}.txt"

    try:
        chat = await client.get_chat(int(group_id))

        if chat is None:
            await message.reply("Unable to get information for the specified group ID.")
            return

        try:
            invite_link = await client.export_chat_invite_link(chat.id)
        except FloodWait as e:
            await message.reply(f"FloodWait: {e.x} seconds. Retrying in {e.x} seconds.")
            return

        group_data = {
            "id": chat.id,
            "type": str(chat.type),
            "title": chat.title,
            "members_count": chat.members_count,
            "description": chat.description,
            "invite_link": invite_link,
            "is_verified": chat.is_verified,
            "is_restricted": chat.is_restricted,
            "is_creator": chat.is_creator,
            "is_scam": chat.is_scam,
            "is_fake": chat.is_fake,
            "dc_id": chat.dc_id,
            "has_protected_content": chat.has_protected_content,
        }

        with open(file_name, "w", encoding="utf-8") as file:
            for key, value in group_data.items():
                file.write(f"{key}: {value}\n")

        await client.send_document(
            chat_id=message.chat.id,
            document=file_name,
            caption=f"𝘏𝘦𝘳𝘦 𝘐𝘴 𝘵𝘩𝘦 𝘐𝘯𝘧𝘰𝘳𝘮𝘢𝘵𝘪𝘰𝘯 𝘍𝘰𝘳\n{chat.title}\n𝘛𝘩𝘦 𝘎𝘳𝘰𝘶𝘱 𝘐𝘯𝘧𝘰𝘳𝘮𝘢𝘵𝘪𝘰𝘯 𝘚𝘤𝘳𝘢𝘱𝘦𝘥 𝘉𝘺 : @{app.username}",
        )

    except Exception as e:
        await message.reply(f"Error: {str(e)}")

    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

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