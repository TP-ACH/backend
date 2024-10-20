import os
import datetime
from typing import Dict
from bson import ObjectId
from motor import motor_asyncio
from pymongo import MongoClient
from pymongo import ReturnDocument

from utils.logger import logger
from models.alert import Alert, AlertUpdate, DBAlert
from models.auth import User

logger.getChild("database")
# MongoDB connection
MONGODB_HOST = os.getenv("MONGODB_HOST")
MONGODB_PORT = os.getenv("MONGODB_PORT")
MONGODB_DB = os.getenv("MONGO_INITDB_DATABASE")
MONGODB_USER = os.getenv("MONGO_INITDB_USER")
MONGODB_PASSWORD = os.getenv("MONGO_INITDB_PASSWORD")

MONGODB_URI = f"mongodb://{MONGODB_USER}:{MONGODB_PASSWORD}@{MONGODB_HOST}:{MONGODB_PORT}/?authSource=admin&retryWrites=true&w=majority"

mongo_client = motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
sync_mongo_client = MongoClient(MONGODB_URI)


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
    data_entry = {"reading": reading, "created_at": datetime.datetime.now()}
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
                    "data": {
                        "$push": {
                            "reading": "$reading",
                            "created_at": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d %H:%M:%S",
                                    "date": "$created_at",
                                    "timezone": "America/Sao_Paulo",
                                }
                            },
                        }
                    },
                }
            },
            {"$project": {"_id": 0, "max": 1, "min": 1, "average": 1, "data": 1}},
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
                "average": None,
            }

    return all_data


async def get_user(username: str):
    db = mongo_client.get_database(MONGODB_DB)
    user_collection = db.get_collection("users")
    user = await user_collection.find_one({"username": username})
    return User(**user) if user else None


async def insert_user(user: User):
    db = mongo_client.get_database(MONGODB_DB)
    user_collection = db.get_collection("users")
    await user_collection.insert_one(user.dict())


async def update_user(user: User, user_update: User):
    db = mongo_client.get_database(MONGODB_DB)
    user_collection = db.get_collection("users")
    updated_user_data = user_update.dict(exclude_unset=True)
    updated_user = await user_collection.find_one_and_update(
        {"username": user.username},
        {"$set": updated_user_data},
        return_document=ReturnDocument.AFTER,
    )
    return User(**updated_user) if updated_user else None


async def insert_species_defaults(defaults):
    db = mongo_client.get_database(MONGODB_DB)
    defaults_collection = db.get_collection("species_defaults")
    await defaults_collection.insert_many([rule.dict() for rule in defaults])


async def get_species_defaults(species):
    db = mongo_client.get_database(MONGODB_DB)
    defaults_collection = db.get_collection("species_defaults")
    rules = await defaults_collection.find_one({"species": species})
    if rules:
        rules.pop("_id", None)
    return rules


async def add_rules_by_device(rules_by_device):
    db = mongo_client.get_database(MONGODB_DB)
    devices_collection = db.get_collection("devices_rules")
    device_rules = await devices_collection.find_one({"device": rules_by_device.device})

    if device_rules:
        await devices_collection.update_one({"device": rules_by_device.device})
    else:
        await devices_collection.insert_one(rules_by_device.dict())


async def update_existing_rule(collection, device, sensor, rule_update):
    logger.info(f"Updating rule with compare: {rule_update.compare}")
    return await collection.update_one(
        {
            "device": device,
            "rules_by_sensor.sensor": sensor,
            "rules_by_sensor.rules.compare": {"$eq": rule_update.compare},
        },
        {"$set": {"rules_by_sensor.$[sensor].rules.$[rule]": rule_update.dict()}},
        array_filters=[
            {"sensor.sensor": sensor},
            {"rule.compare": rule_update.compare},
        ],
    )


async def add_rule_existing_sensor(collection, device, sensor, rule):
    return await collection.update_one(
        {"device": device, "rules_by_sensor.sensor": sensor},
        {"$push": {"rules_by_sensor.$.rules": rule.dict()}},
    )


async def add_new_sensor_with_rules(collection, device, sensor_rules):
    return await collection.update_one(
        {"device": device}, {"$push": {"rules_by_sensor": sensor_rules.dict()}}
    )

async def update_device_species(rules_by_device, devices_collection):
    logger.info(f"Updating selected species for device: {rules_by_device.device}")
    updated = await devices_collection.update_one(
        {
            "device": rules_by_device.device,
        },
        {"$set": {"species": rules_by_device.species}},
    )
    if updated.matched_count == 0:
        logger.info(f"Inserting new device entry for {rules_by_device.device}")
        await devices_collection.insert_one(rules_by_device.dict())

async def update_sensor_rules(rules_by_device, devices_collection):
    for sensor_update in rules_by_device.rules_by_sensor:
        logger.info(f"Updating rules for sensor: {sensor_update.sensor}")
        for rule_update in sensor_update.rules:
            updated = await update_existing_rule(
                devices_collection,
                rules_by_device.device,
                sensor_update.sensor,
                rule_update,
            )
            if updated.matched_count == 0:
                logger.info(
                    f"Rule not found for sensor {sensor_update.sensor}, compare {rule_update.compare}. Pushing new rule."
                )
                await add_rule_existing_sensor(
                    devices_collection,
                    rules_by_device.device,
                    sensor_update.sensor,
                    rule_update,
                )

        sensor_exists = await devices_collection.find_one(
            {
                "device": rules_by_device.device,
                "rules_by_sensor.sensor": sensor_update.sensor,
            }
        )
        if not sensor_exists:
            logger.info(
                f"Sensor {sensor_update.sensor} not found. Adding new sensor with rules."
            )
            added = await add_new_sensor_with_rules(
                devices_collection, rules_by_device.device, sensor_update
            )
            if added.matched_count == 0:
                logger.info(f"Inserting new device entry for {rules_by_device.device}")
                await devices_collection.insert_one(rules_by_device.dict())


async def update_light_hours(rules_by_device, devices_collection):
    logger.info(f"Updating light hours for device: {rules_by_device.device}")
    updated = await devices_collection.update_one(
        {
            "device": rules_by_device.device,
        },
        {"$set": {"light_hours": rules_by_device.light_hours.dict()}},
    )
    if updated.matched_count == 0:
        logger.info(f"Inserting new device entry for {rules_by_device.device}")
        await devices_collection.insert_one(rules_by_device.dict())


async def update_rules_by_device(rules_by_device):
    db = mongo_client.get_database(MONGODB_DB)
    devices_collection = db.get_collection("devices_rules")
    if rules_by_device.species:
        await update_device_species(rules_by_device, devices_collection)
    if rules_by_device.rules_by_sensor:
        await update_sensor_rules(rules_by_device, devices_collection)
    if rules_by_device.light_hours:
        await update_light_hours(rules_by_device, devices_collection)
    return True


async def get_device_rules(device_id: str):
    db = mongo_client.get_database(MONGODB_DB)
    devices_collection = db.get_collection("devices_rules")

    rules = await devices_collection.find_one({"device": device_id})
    if rules:
        rules.pop("_id", None)
    return rules


async def get_sensor_rules(device_id: str, sensor: str):
    db = mongo_client.get_database(MONGODB_DB)
    devices_collection = db.get_collection("devices_rules")

    device_rules = await devices_collection.find_one(
        {"device": device_id, "rules_by_sensor.sensor": sensor}
    )
    if not device_rules:
        return None
    sensor_rules = next(
        (s for s in device_rules["rules_by_sensor"] if s["sensor"] == sensor), None
    )
    return sensor_rules


def sync_get_sensor_rules(device_id: str, sensor: str):
    db = sync_mongo_client.get_database(MONGODB_DB)
    devices_collection = db.get_collection("devices_rules")

    device_rules = devices_collection.find_one(
        {"device": device_id, "rules_by_sensor.sensor": sensor}
    )
    if not device_rules:
        return None
    sensor_rules = next(
        (s for s in device_rules["rules_by_sensor"] if s["sensor"] == sensor), None
    )
    return sensor_rules


async def read_alerts(
    device_id=None, type=None, status=None, topic=None
) -> list[Alert]:
    db = mongo_client.get_database(MONGODB_DB)
    alert_collection = db.get_collection("alerts")

    filter = {
        "device_id": device_id,
        "type": type.value if type else None,
        "status": status.value if status else None,
        "topic": topic.value if topic else None,
    }
    filter = {k: v for k, v in filter.items() if v is not None}

    alerts_cursor = alert_collection.find(filter)
    alerts = await alerts_cursor.to_list(length=None)

    return [DBAlert(**{**alert, "_id": str(alert["_id"])}) for alert in alerts]


def sync_read_alerts(device_id=None, type=None, status=None, topic=None) -> list[Alert]:
    db = sync_mongo_client.get_database(MONGODB_DB)
    alert_collection = db.get_collection("alerts")

    filter = {
        "device_id": device_id,
        "type": type.value if type else None,
        "status": status.value if status else None,
        "topic": topic.value if topic else None,
    }
    filter = {k: v for k, v in filter.items() if v is not None}

    alerts_cursor = alert_collection.find(filter)

    return [
        DBAlert(**{**alert, "_id": str(alert["_id"])}) for alert in list(alerts_cursor)
    ]


async def insert_alert(alert) -> Alert:
    db = mongo_client.get_database(MONGODB_DB)
    alert_collection = db.get_collection("alerts")

    alert_dict = alert.dict(by_alias=True, exclude={"id"})
    alert_dict["type"] = alert.type.value
    alert_dict["status"] = alert.status.value
    alert_dict["topic"] = alert.topic.value

    result = await alert_collection.insert_one(alert_dict)

    alert.id = str(result.inserted_id)
    return alert


def sync_insert_alert(alert) -> Alert:
    db = sync_mongo_client.get_database(MONGODB_DB)
    alert_collection = db.get_collection("alerts")

    alert_dict = alert.dict(by_alias=True, exclude={"id"})
    alert_dict["type"] = alert.type.value
    alert_dict["status"] = alert.status.value
    alert_dict["topic"] = alert.topic.value

    result = alert_collection.insert_one(alert_dict)

    alert.id = str(result.inserted_id)
    return alert


async def update_alert(alert: AlertUpdate):
    db = mongo_client.get_database(MONGODB_DB)
    alert_collection = db.get_collection("alerts")

    filter = {"_id": ObjectId(alert.id)}

    update_data = {
        k: v for k, v in alert.dict(exclude_unset=True).items() if k != "id" and v
    }

    result = await alert_collection.update_one(filter, {"$set": update_data})

    return result.modified_count > 0 or result.matched_count > 0


async def delete_alert(id: str):
    db = mongo_client.get_database(MONGODB_DB)
    alert_collection = db.get_collection("alerts")

    result = await alert_collection.delete_one({"_id": ObjectId(id)})
    return result.deleted_count > 0

async def fetch_devices():
    devices = await mongo_client.list_database_names()
    excluded_databases = ["admin", "config", "local", MONGODB_DB]
    filtered_devices = [db for db in devices if db not in excluded_databases]
    return filtered_devices


async def get_latest_sensor_readings():
    latest_readings = {}
    databases = await mongo_client.list_database_names()

    for db_name in databases:
        if db_name in ["admin", "config", "local", os.getenv("MONGO_INITDB_DATABASE")]:
            continue

        db = mongo_client.get_database(db_name)
        latest_readings[db_name] = {}
        sensors = await db.list_collection_names()

        for sensor in sensors:
            collection = db.get_collection(sensor)
            pipeline = [
                {"$sort": {"created_at": -1}},
                {
                    "$group": {
                        "_id": None,
                        "reading": {"$first": "$reading"},
                        "created_at": {
                            "$first": {
                                "$dateToString": {
                                    "format": "%Y-%m-%d %H:%M:%S",
                                    "date": "$created_at",
                                    "timezone": "America/Sao_Paulo",
                                }
                            }
                        },
                    }
                },
                {"$project": {"_id": 0, "reading": 1, "created_at": 1}},
            ]

            latest_entry = await collection.aggregate(pipeline).to_list(length=None)

            if latest_entry:
                latest_readings[db_name][sensor] = latest_entry

    return latest_readings
