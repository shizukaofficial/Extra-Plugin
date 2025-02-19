from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ChampuMusic import app
from datetime import datetime, timedelta
import asyncio

# User data and state management
user_data = {}

# Define states for the FSM
class State:
    WAITING_FOR_PHOTO = 1
    WAITING_FOR_CAPTION = 2
    WAITING_FOR_BUTTONS_CONFIRMATION = 3
    WAITING_FOR_BUTTON_COUNT = 4
    WAITING_FOR_BUTTON_DATA = 5

# Helper function to clear user data
def clear_user_data(chat_id):
    if chat_id in user_data:
        del user_data[chat_id]

# Command to start the sharing process
@app.on_message(filters.command("share"))
async def share_command(client, message):
    chat_id = message.chat.id
    user_data[chat_id] = {'state': State.WAITING_FOR_PHOTO, 'timestamp': datetime.now()}
    await message.reply("Please send the image/photo for your share message.")

# Handle photo messages
@app.on_message(filters.photo)
async def receive_photo(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data or user_data[chat_id]['state'] != State.WAITING_FOR_PHOTO:
        return
    
    user_data[chat_id]['photo'] = message.photo.file_id
    user_data[chat_id]['state'] = State.WAITING_FOR_CAPTION
    await message.reply("Great! Now, send me the caption.")

# Handle text messages (captions and button data)
@app.on_message(filters.text & ~filters.command("share"))
async def receive_text(client, message):
    chat_id = message.chat.id
    if chat_id not in user_data:
        return
    
    data = user_data[chat_id]
    current_state = data['state']
    
    if current_state == State.WAITING_FOR_CAPTION:
        data['caption'] = message.text
        data['state'] = State.WAITING_FOR_BUTTONS_CONFIRMATION
        await message.reply("Do you want to add buttons? (Yes/No)")
    
    elif current_state == State.WAITING_FOR_BUTTONS_CONFIRMATION:
        if message.text.lower() == "yes":
            data['state'] = State.WAITING_FOR_BUTTON_COUNT
            await message.reply("How many buttons do you want to add?")
        elif message.text.lower() == "no":
            await send_final_message(client, chat_id)
        else:
            await message.reply("Please respond with 'Yes' or 'No'.")
    
    elif current_state == State.WAITING_FOR_BUTTON_COUNT:
        try:
            button_count = int(message.text)
            if button_count <= 0:
                await message.reply("Please send a positive number.")
                return
            data['button_count'] = button_count
            data['buttons'] = []
            data['current_button'] = 1
            data['state'] = State.WAITING_FOR_BUTTON_DATA
            await message.reply(f"Send the name and link for button {data['current_button']} (Format: Name | URL)")
        except ValueError:
            await message.reply("Please send a valid number.")
    
    elif current_state == State.WAITING_FOR_BUTTON_DATA:
        parts = message.text.split("|")
        if len(parts) == 2:
            name, url = parts[0].strip(), parts[1].strip()
            data['buttons'].append([InlineKeyboardButton(name, url=url)])
            
            if len(data['buttons']) == data['button_count']:
                await send_final_message(client, chat_id)
            else:
                data['current_button'] += 1
                await message.reply(f"Send the name and link for button {data['current_button']} (Format: Name | URL)")
        else:
            await message.reply("Invalid format! Use: Name | URL")

# Send the final message with photo, caption, and buttons
async def send_final_message(client, chat_id):
    data = user_data.pop(chat_id, None)
    if not data:
        return

    buttons = data.get('buttons', [])
    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    
    await client.send_photo(
        chat_id=chat_id,
        photo=data['photo'],
        caption=data['caption'],
        reply_markup=reply_markup
    )
    clear_user_data(chat_id)
# Timeout handling (optional)
async def check_timeouts():
    while True:
        now = datetime.now()
        for chat_id, data in list(user_data.items()):
            if now - data['timestamp'] > timedelta(minutes=5):  # 5-minute timeout
                clear_user_data(chat_id)
                await app.send_message(chat_id, "Session timed out. Please start again.")
        await asyncio.sleep(60)  # Check every minute

# Run the timeout checker in the background
asyncio.create_task(check_timeouts())


MODULE = "Share"
HELP = """
/share - Start the sharing process by sending an image.
Follow the prompts to add a caption and optional buttons to your share message.
"""