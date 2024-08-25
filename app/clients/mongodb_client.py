import os
import datetime
from typing import Dict
from motor import motor_asyncio
from utils.logger import logger

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
        logger.info(MONGODB_URI)
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


async def insert_ha_data(db_name, collection, data):
    db = mongo_client.get_database(db_name)
    data_collection = db.get_collection(collection)
    await data_collection.insert_many(data)

async def fetch_data(device_id: str, sensor: str, query: Dict):
    db = mongo_client.get_database(device_id)
    collection_names = await db.list_collection_names()
    
    all_data = {}
    
    for collection_name in collection_names:
        if sensor and sensor != collection_name:
            continue
        collection = db.get_collection(collection_name)

        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": None,
                    "max": {"$max": "$reading"},
                    "min": {"$min": "$reading"},
                    "average": {"$avg": "$reading"},
                    "data": {"$push": {"reading": "$reading", "created_at": "$created_at"}}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "max": 1,
                    "min": 1,
                    "average": 1,
                    "data": 1
                }
            }
        ]
        
        cursor = collection.aggregate(pipeline)
        result = await cursor.to_list(length=None)
        
        if result:
            all_data[collection_name] = result[0]
        else:
            all_data[collection_name] = {
                "data": [],
                "max": None,
                "min": None,
                "average": None
            }
    
    return all_data