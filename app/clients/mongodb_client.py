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

async def insert_species_defaults(defaults):
    db = mongo_client.get_database("fastapi")
    defaults_collection = db.get_collection("species_defaults")
    await defaults_collection.insert_many([rule.dict() for rule in defaults])

async def insert_rules_by_device(rules):
    db = mongo_client.get_database("fastapi")
    defaults_collection = db.get_collection("species_defaults")
    rules_collection = db.get_collection("rules")
    
async def get_species_defaults(species):
    db = mongo_client.get_database("fastapi")
    defaults_collection = db.get_collection("species_defaults")
    rules =  await defaults_collection.find_one({"species": species})
    if rules:
        rules.pop("_id", None)
    return rules

async def add_rules_by_device(rules_by_device):
    db = mongo_client.get_database("fastapi")
    devices_collection = db.get_collection("devices_rules")
    device_rules =  await devices_collection.find_one({"device": rules_by_device.device})
    
    if device_rules:
        await devices_collection.update_one(
            {"device": rules_by_device.device}
            )
    else:
        await devices_collection.insert_one(rules_by_device.dict())
        
async def update_rules_by_device(rules_by_device):
    db = mongo_client.get_database("fastapi")
    devices_collection = db.get_collection("devices_rules")
    
    for sensor_update in rules_by_device.rules_by_sensor:
        logger.info(f"Updating rules for sensor: {sensor_update.sensor}")
        for rule_update in sensor_update.rules:
            logger.info(f"Updating rule with compare: {rule_update.compare}")
            updated = await devices_collection.update_one(
                {
                    "device": rules_by_device.device,
                    "rules_by_sensor.sensor": sensor_update.sensor,
                    "rules_by_sensor.rules.compare": {"$eq": rule_update.compare}
                },
                {
                    "$set": {
                        "rules_by_sensor.$[sensor].rules.$[rule]": rule_update.dict()
                    }
                },
                array_filters=[
                    {"sensor.sensor": sensor_update.sensor},
                    {"rule.compare": rule_update.compare}
                ]
            )
            if updated.matched_count == 0:
                logger.info(f"Rule not found for sensor {sensor_update.sensor}, compare {rule_update.compare}. Pushing new rule.")
                await devices_collection.update_one(
                    {"device": rules_by_device.device, "rules_by_sensor.sensor": sensor_update.sensor},
                    {
                        "$push": {
                            "rules_by_sensor.$.rules": rule_update.dict()
                        }
                    }
                )
        
        sensor_exists = await devices_collection.find_one(
            {"device": rules_by_device.device, "rules_by_sensor.sensor": sensor_update.sensor}
        )
        
        if not sensor_exists:
            logger.info(f"Sensor {sensor_update.sensor} not found. Adding new sensor with rules.")
            added = await devices_collection.update_one(
                {"device": rules_by_device.device},
                {
                    "$push": {
                        "rules_by_sensor": sensor_update.dict()
                    }
                }
            )
            logger.info(f"Added sensor result: {added}")
            if added.matched_count == 0:
                logger.info(f"Inserting new device entry for {rules_by_device.device}")
                await devices_collection.insert_one(rules_by_device.dict())
    return {"message": "Device rules updated or added successfully"}