from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from ChampuMusic import app
from pyrogram.errors import UserNotParticipant
from ChampuMusic.misc import SUDOERS
from config import LOGGER_ID
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from config import MONGO_DB_URI
import logging
import asyncio


logger = logging.getLogger(__name__)

# Database connection with connection pooling
_client = None

def get_database():
    global _client
    if not _client:
        _client = AsyncIOMotorClient(MONGO_DB_URI, maxPoolSize=100, minPoolSize=10)
        logger.info("Connected to MongoDB with connection pooling")
        # Schedule the create_indexes coroutine to run in the event loop
        asyncio.create_task(create_indexes(_client["ChampuMusic"]))
    return _client["ChampuMusic"]


async def create_indexes(db):
    """Create database indexes if they don't exist"""
    await db.conversations.create_index(
        [("forwarded_msg_id", 1)], 
        unique=True,
        background=True
    )
    await db.conversations.create_index(
        [("timestamp", 1)],
        expireAfterSeconds=604800,  # 7 days TTL
        background=True
    )
    logger.info("Created database indexes")



async def verify_connection():
    """Verify database connection is working"""
    try:
        db = get_database()
        await db.command('ping')
        logger.info("Database connection verified")
        return True
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False


async def store_conversation(original_user: int, forwarded_msg_id: int):

    """Store conversation mapping in database"""
    db = get_database()
    await db.conversations.insert_one({
        "original_user": original_user,
        "forwarded_msg_id": forwarded_msg_id,
        "timestamp": datetime.now()
    })

async def get_original_user(forwarded_msg_id: int) -> int | None:
    """Get original user ID from forwarded message ID
    Returns: User ID or None if not found
    """
    db = get_database()
    conversation = await db.conversations.find_one(
        {"forwarded_msg_id": forwarded_msg_id},
        {"_id": 0, "original_user": 1}
    )
    return conversation.get("original_user") if conversation else None

# Message forwarding handler
@app.on_message(filters.private & ~filters.me & ~filters.command("send"))
async def forward_to_admin(client: Client, message: Message):
    """Forward user messages to admin"""
    try:
        # Forward message to admin
        forwarded_msg = await message.forward(LOGGER_ID)
        # Store conversation context
        await store_conversation(
            original_user=message.from_user.id,
            forwarded_msg_id=forwarded_msg.id
        )
    except Exception as e:
        await message.reply_text(f"Error forwarding message: {e}")

# Admin reply handler
@app.on_message(filters.private & filters.me & filters.reply)
async def handle_admin_reply(client: Client, message: Message):
    """Forward admin replies back to original user"""
    try:
        original_user = await get_original_user(message.reply_to_message.id)
        if original_user:
            await client.send_message(
                chat_id=original_user,
                text=message.text,
                reply_to_message_id=message.reply_to_message.id
            )
        else:
            await message.reply_text("No original user found for this message")
    except Exception as e:
        await message.reply_text(f"Error handling reply: {e}")

@app.on_message(filters.command("send") & SUDOERS)
async def send_message(client, message):
    # Check if the command has the correct number of arguments
    if len(message.command) < 2:
        await message.reply_text("ᴜsᴀɢᴇ: /send <username or group_id> <message> (or reply to a message with /send <username or group_id>)")
        return

    target = message.command[1]

    # If the command is a reply, use the replied message
    if message.reply_to_message:
        try:
            # Check if the bot is a member of the target chat
            bot_member = await client.get_chat_member(chat_id=target, user_id=client.me.id)
            if bot_member.status in ["left", "kicked"]:
                await message.reply_text("ɪ ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ ғɪʀsᴛ.")
                return

            # Forward or copy the replied message
            sent_message = await message.reply_to_message.copy(chat_id=target)

            chat_id = sent_message.chat.id
            message_id = sent_message.id
            message_url = f"https://t.me/c/{str(chat_id)[4:]}/{message_id}"

            view_button = InlineKeyboardButton(" ɢʀᴏᴜᴘ ", url=f"https://t.me/{target}")
            mention_button = InlineKeyboardButton(" ᴍᴇssᴀɢᴇ ", url=message_url)
            reply_markup = InlineKeyboardMarkup([[view_button, mention_button]])

            await message.reply_text("ᴍᴇssᴀɢᴇ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!", reply_markup=reply_markup)

        except UserNotParticipant:
            await message.reply_text("ɪ ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ ғɪʀsᴛ.")
        except Exception as e:
            await message.reply_text(f"ᴇʀʀᴏʀ: {e}")
        return

    # If not a reply, send as text as before
    if len(message.command) < 3:
        await message.reply_text("ᴜsᴀɢᴇ: /send <username or group_id> <message>")
        return

    msg_content = " ".join(message.command[2:])

    try:
        bot_member = await client.get_chat_member(chat_id=target, user_id=client.me.id)
        if bot_member.status in ["left", "kicked"]:
            await message.reply_text("ɪ ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ ғɪʀsᴛ.")
            return

        sent_message = await client.send_message(chat_id=target, text=msg_content)

        chat_id = sent_message.chat.id
        message_id = sent_message.id
        message_url = f"https://t.me/c/{str(chat_id)[4:]}/{message_id}"

        view_button = InlineKeyboardButton(" ɢʀᴏᴜᴘ ", url=f"https://t.me/{target}")
        mention_button = InlineKeyboardButton(" ᴍᴇssᴀɢᴇ ", url=message_url)
        reply_markup = InlineKeyboardMarkup([[view_button, mention_button]])

        await message.reply_text("ᴍᴇssᴀɢᴇ sᴇɴᴛ sᴜᴄᴄᴇssғᴜʟʟʏ!", reply_markup=reply_markup)

    except UserNotParticipant:
        await message.reply_text("ɪ ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ. ᴘʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ ғɪʀsᴛ.")
    except Exception as e:
        await message.reply_text(f"ᴇʀʀᴏʀ: {e}")
