import time
import random
from datetime import datetime, timedelta

import pyrogram
from pyrogram import filters

from ChampuMusic import app
from ChampuMusic.misc import SUDOERS

# Cooldown dictionary to prevent spam abuse
cooldown = {}

# Predefined spam messages for randomization
SPAM_MESSAGES = [
    "sᴘᴀᴍ!",
    "ʀᴀɪᴅ!",
    "ʙᴏᴏᴍ!",
    "ᴘᴇᴡ ᴘᴇᴡ!",
    "ʙᴀɴɢ!",
]

# Define the raid command handler
@app.on_message(filters.command("raid", prefixes="/") & SUDOERS)
async def raid_command(client, message):
    user_id = message.from_user.id
    current_time = datetime.now()

    # Check if the user is on cooldown
    if user_id in cooldown and current_time < cooldown[user_id]:
        time_left = (cooldown[user_id] - current_time).seconds
        await message.reply_text(f"ʏᴏᴜ ᴀʀᴇ ᴏɴ ᴄᴏᴏʟᴅᴏᴡɴ. ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪɴ {time_left} sᴇᴄᴏɴᴅs.")
        return

    try:
        # Delete the user's command text
        await message.delete()
    except pyrogram.errors.exceptions.FloodWait as e:
        print(f"ᴇʀʀᴏʀ ᴅᴇʟᴇᴛɪɴɢ ᴍᴇssᴀɢᴇ: {e}")
        pass  # Ignore the deletion error and continue

    # Check if the message is a reply and has text
    if message.reply_to_message and message.reply_to_message.text:
        user_to_tag = message.reply_to_message.from_user.mention()
        command_args = message.text.split("/raid", 1)[-1].strip()

        # Parse the command arguments
        try:
            args = command_args.split()
            if len(args) >= 2:
                num_times = int(args[0])
                delay = float(args[1])
                text_to_spam = " ".join(args[2:]) if len(args) > 2 else random.choice(SPAM_MESSAGES)
            else:
                num_times = 5  # Default number of spam messages
                delay = 0.2  # Default delay between messages
                text_to_spam = random.choice(SPAM_MESSAGES)
        except ValueError:
            await message.reply_text("ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀᴍᴀᴛ. ᴜsᴇ: /raid <num_times> <delay> <text>")
            return

        for _ in range(num_times):
            # Send the spam message to the Telegram chat and mention the user
            await message.reply_text(f"{user_to_tag} **{text_to_spam}**")
            time.sleep(delay)  # Add a delay between spam messages

    elif message.reply_to_message:
        # If no text is provided with the raid command, spam the replied user's message
        user_to_tag = message.reply_to_message.from_user.mention()

        for _ in range(5):  # Default number of spam messages
            await message.reply_to_message.reply_text(f"{user_to_tag} **{random.choice(SPAM_MESSAGES)}**")
            time.sleep(0.2)  # Default delay between spam messages

    else:
        await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴜsᴇ ᴛʜᴇ /raid ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ sᴘᴀᴍ.")

    # Set cooldown for the user
    cooldown[user_id] = current_time + timedelta(minutes=5)  # 5 minutes cooldown

    # Log the raid command usage
    log_message = f"ʀᴀɪᴅ ᴄᴏᴍᴍᴀɴᴅ ᴜsᴇᴅ ʙʏ {message.from_user.mention()} ᴏɴ {user_to_tag} ᴀᴛ {current_time}"
    print(log_message)

__MODULE__ = "Rᴀɪᴅ"
__HELP__ = """
- `/raid <num_times> <delay> <text>`: Rᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴀɴᴅ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ �ᴏ sᴘᴀᴍ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ᴡɪᴛʜ ᴛʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ ᴛᴇxᴛ.
  - `<num_times>`: Nᴜᴍʙᴇʀ ᴏғ ᴛɪᴍᴇs ᴛᴏ sᴘᴀᴍ.
  - `<delay>`: Dᴇʟᴀʏ ʙᴇᴛᴡᴇᴇɴ ᴇᴀᴄʜ sᴘᴀᴍ ᴍᴇssᴀɢᴇ (ɪɴ sᴇᴄᴏɴᴅs).
  - `<text>`: Tᴇxᴛ ᴛᴏ sᴘᴀᴍ (ᴏᴘᴛɪᴏɴᴀʟ, ᴅᴇғᴀᴜʟᴛs ᴛᴏ ʀᴀɴᴅᴏᴍ ᴍᴇssᴀɢᴇs).
"""