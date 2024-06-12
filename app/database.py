import os
import asyncio
from motor import motor_asyncio
from logger import logger

logger.getChild("database")
# MongoDB connection
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_DB = os.getenv("MONGO_INITDB_DATABASE")
MONGODB_USER = os.getenv("MONGO_INITDB_USER")
MONGODB_PASSWORD = os.getenv("MONGO_INITDB_PASSWORD")

MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/{MONGODB_DB}?retryWrites=true&w=majority"

mongo_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
db = mongo_client.get_database(MONGODB_DB)

async def validate_connection():
    try:
        info = await mongo_client.server_info()
        logger.info(f"Connected to MongoDB: {info}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")



def get_collection(collection_name: str):
    return db.get_collection(collection_name)
