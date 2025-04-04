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
        asyncio.run(create_indexes(_client["ChampuMusic"]))
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
