import os
import datetime
from typing import Dict
from motor import motor_asyncio
from logger import logger

logger.getChild("database")
# MongoDB connection
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_DB = os.getenv("MONGO_INITDB_DATABASE")
MONGODB_USER = os.getenv("MONGO_INITDB_USER")
MONGODB_PASSWORD = os.getenv("MONGO_INITDB_PASSWORD")

MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/?authSource=admin&retryWrites=true&w=majority"

mongo_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URI)

async def validate_connection():
    try:
        info = await mongo_client.server_info()
        logger.info(f"Connected to MongoDB: {info}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")


def insert_data(db_name, collection, reading):
    db = mongo_client.get_database(db_name)
    data_collection = db.get_collection(collection)
    data_entry = {
        "reading": reading,
        "created_at": datetime.datetime.now()
    }
    data_collection.insert_one(data_entry)

async def fetch_data(device_id: str, query: Dict):
    db = mongo_client.get_database(device_id)
    collection_names = await db.list_collection_names()
    
    all_data = {}
    
    for collection_name in collection_names:
        collection = db.get_collection(collection_name)
        projection = {"reading": 1, "created_at": 1, "_id": 0}
        cursor = collection.find(query, projection)
        all_data[collection_name] = await cursor.to_list(length=None)
    
    return all_data