from pyrogram.handlers import ChatMemberUpdatedHandler
from pyrogram.types import ChatMemberUpdated, Message
from typing import Union, List
from pyrogram import Client, filters
from ChampuMusic import app
from pytgcalls import StreamType
from pytgcalls.exceptions import NoActiveCallError, AlreadyJoinedGroupCallError  # Updated import
from pytgcalls.types.input_stream import AudioPiped
import asyncio
from ChampuMusic.core.call import Champu
from ChampuMusic.utils.database import group_assistant

# Default state for /infovc
infovc_enabled = False  # Default disabled

def command(commands: Union[str, List[str]]):
    return filters.command(commands, prefixes=["/"])

@app.on_message(command(["infovc"]))
async def toggle_infovc(client: Client, message: Message):
    global infovc_enabled
    if len(message.command) > 1:
        state = message.command[1].lower()
        if state == "on":
            infovc_enabled = True
            await message.reply("✅ Voice chat join notifications are now enabled.")
        elif state == "off":
            infovc_enabled = False
            await message.reply("❌ Voice chat join notifications are now disabled.")
        else:
            await message.reply("⚠️ Usage: /infovc on or /infovc off")
    else:
        await message.reply("⚠️ Usage: /infovc on or /infovc off")

@app.on_message(filters.command(["vcinfo"], ["/", "!"]))
async def strcall(client, message):
    assistant = await group_assistant(Champu, message.chat.id)
    try:
        await assistant.join_group_call(
            message.chat.id,
            AudioPiped("./ChampuMusic/assets/call.mp3"),
            stream_type=StreamType().pulse_stream
        )
        participants = await assistant.get_participants(message.chat.id)
        text = "- Participants in the call 🫶 :\n\n"
        
        for index, participant in enumerate(participants, start=1):
            user = await client.get_users(participant.user_id)
            mute_status = "🎤 Unmuted" if not participant.muted else "🔇 Muted"
            muter = "Unknown"
            if participant.muted_by:
                muter_user = await client.get_users(participant.muted_by)
                muter = muter_user.mention
            text += f"{index} ➤ {user.mention} ➤ {mute_status} (Muted by: {muter})\n"
        
        text += f"\nTotal participants: {len(participants)}"
        await message.reply(text)
        await asyncio.sleep(7)
        await assistant.leave_group_call(message.chat.id)
    
    except NoActiveCallError:  # Updated exception
        await message.reply("No active group call found. Please start a voice chat first.")
    except AlreadyJoinedGroupCallError:
        participants = await assistant.get_participants(message.chat.id)
        text = "Participants in the call 🫶 :\n\n"
        for index, participant in enumerate(participants, start=1):
            user = await client.get_users(participant.user_id)
            mute_status = "🎤 Unmuted" if not participant.muted else "🔇 Muted"
            muter = "Unknown"
            if participant.muted_by:
                muter_user = await client.get_users(participant.muted_by)
                muter = muter_user.mention
            text += f"{index} ➤ {user.mention} ➤ {mute_status} (Muted by: {muter})\n"
        text += f"\nTotal participants: {len(participants)}"
        await message.reply(text)
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

async def user_joined_voice_chat(client: Client, chat_member_updated: ChatMemberUpdated):
    global infovc_enabled
    if not infovc_enabled:
        return
    try:
        chat = chat_member_updated.chat
        user = chat_member_updated.new_chat_member.user
        if not chat or not user:
            return
        old_status = chat_member_updated.old_chat_member.status
        new_status = chat_member_updated.new_chat_member.status
        if old_status in ["left", "kicked", "member"] and new_status == "voice_chat_participant":
            text = (
                f"**#JoinVoiceChat**\n"
                f"👤 **Name:** {user.mention}\n"
                f"🆔 **ID:** `{user.id}`\n"
                f"🎤 **Action:** Joined the voice chat"
            )
            await client.send_message(chat.id, text)
    except Exception as e:
        print(f"⚠️ Error in user_joined_voice_chat: {e}")

app.add_handler(ChatMemberUpdatedHandler(user_joined_voice_chat))