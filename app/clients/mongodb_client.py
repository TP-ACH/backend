import os
import datetime
from typing import Dict
from exceptions.not_found_exception import NotFoundException
from models.model_type import ModelType
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


async def get_ha_data_by_model(automation_name: str, model: ModelType):
    logger.info(f"Fetching data for {automation_name} from {model.name}")
    db = mongo_client.get_database(MONGODB_DB)
    collection = db.get_collection(model.name)
    result = await collection.find_one({"name": automation_name}, sort=[("last_modified", -1)])
    if result is None:
        raise NotFoundException(f"{automation_name} not found")
    return result

async def add_ha_data_by_model(data, model: ModelType):
    db = mongo_client.get_database(MONGODB_DB)
    collection = db.get_collection(model.name)
    data_entry = {
        "name": data.alias,
        "data": data.model_dump(),
        "last_modified": datetime.datetime.now()
    }
    return await collection.insert_one(data_entry)

async def insert_ha_data(collection, data):
    db = mongo_client.get_database(MONGODB_DB)
    data_collection = db.get_collection(f"local_{collection}")
    await data_collection.insert_many(data)

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