import os
import datetime
from typing import Dict
from motor import motor_asyncio
from utils.logger import logger
from models.auth import UserInDB

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
                    "data": {"$push": {
                        "reading": "$reading",
                        "created_at": {"$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$created_at", "timezone": "America/Sao_Paulo"}}
                    }}
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


async def get_user(username: str):
    db = mongo_client.get_database("Users")
    user_collection = db.get_collection("active")
    user = await user_collection.find_one({"username": username})
    return UserInDB(**user) if user else None
    

async def insert_user(user):
    db = mongo_client.get_database("Users")
    user_collection = db.get_collection("active")
    await user_collection.insert_one(user.dict())

async def insert_species_defaults(defaults):
    db = mongo_client.get_database("fastapi")
    defaults_collection = db.get_collection("species_defaults")
    await defaults_collection.insert_many([rule.dict() for rule in defaults])
    
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
        
async def update_existing_rule(collection, device, sensor, rule_update):
    logger.info(f"Updating rule with compare: {rule_update.compare}")
    return await collection.update_one(
                {
                    "device": device,
                    "rules_by_sensor.sensor": sensor,
                    "rules_by_sensor.rules.compare": {"$eq": rule_update.compare}
                },
                {
                    "$set": {
                        "rules_by_sensor.$[sensor].rules.$[rule]": rule_update.dict()
                    }
                },
                array_filters=[
                    {"sensor.sensor": sensor},
                    {"rule.compare": rule_update.compare}
                ]
            )
    
async def add_rule_existing_sensor(collection, device, sensor, rule):
    return await collection.update_one(
                    {"device": device, "rules_by_sensor.sensor": sensor},
                    {
                        "$push": {
                            "rules_by_sensor.$.rules": rule.dict()
                        }
                    }
                )
    
async def add_new_sensor_with_rules(collection, device, sensor_rules):
    return await collection.update_one(
                {"device": device},
                {
                    "$push": {
                        "rules_by_sensor": sensor_rules.dict()
                    }
                }
            )

async def update_rules_by_device(rules_by_device):
    db = mongo_client.get_database("fastapi")
    devices_collection = db.get_collection("devices_rules")
    
    for sensor_update in rules_by_device.rules_by_sensor:
        logger.info(f"Updating rules for sensor: {sensor_update.sensor}")
        for rule_update in sensor_update.rules:
            updated = await update_existing_rule(devices_collection, rules_by_device.device, sensor_update.sensor, rule_update)
            if updated.matched_count == 0:
                logger.info(f"Rule not found for sensor {sensor_update.sensor}, compare {rule_update.compare}. Pushing new rule.")
                await add_rule_existing_sensor(devices_collection, rules_by_device.device, sensor_update.sensor, rule_update)
        
        sensor_exists = await devices_collection.find_one(
            {"device": rules_by_device.device, "rules_by_sensor.sensor": sensor_update.sensor}
        )
        if not sensor_exists:
            logger.info(f"Sensor {sensor_update.sensor} not found. Adding new sensor with rules.")
            added = await add_new_sensor_with_rules(devices_collection, rules_by_device.device, sensor_update)
            if added.matched_count == 0:
                logger.info(f"Inserting new device entry for {rules_by_device.device}")
                await devices_collection.insert_one(rules_by_device.dict())
    return True

async def get_device_rules(device_id: str):
    db = mongo_client.get_database("fastapi")
    devices_collection = db.get_collection("devices_rules")
    
    rules = await devices_collection.find_one({"device": device_id})
    if rules:
        rules.pop("_id", None)
    return rules