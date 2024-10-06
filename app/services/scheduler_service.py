import pytz
from datetime import datetime
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo import MongoClient

from clients.mongodb_client import MONGODB_DB
from clients.mongodb_client import MONGODB_URI
from controllers.mqtt_controller import mqtt_client
from utils.consts import TIMEZONE
from utils.consts import SWITCH_LIGHT_OFF_TOPIC
from utils.consts import SWITCH_LIGHT_ON_TOPIC
from utils.logger import logger

timezone = pytz.timezone(TIMEZONE)

sync_mongo_client = MongoClient(MONGODB_URI)
jobstores = {
    "default": MongoDBJobStore(
        database=MONGODB_DB, collection="jobs", client=sync_mongo_client
    )
}

scheduler = AsyncIOScheduler(jobstores=jobstores)
scheduler.start()
logger.info("Scheduler started")


def schedule_light_cycle(device_id, start_time, end_time):
    try:
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.strptime(end_time, "%H:%M").time()
    except ValueError:
        logger.error("Invalid time format. Please use HH:MM")
    scheduler.remove_job(f"on_{device_id}")
    scheduler.remove_job(f"off_{device_id}")

    scheduler.add_job(
        turn_on_light,
        "cron",
        hour=start_time.hour,
        minute=start_time.minute,
        second=start_time.second,
        timezone=timezone,
        args=[device_id],
        id=f"on_{device_id}",
    )

    scheduler.add_job(
        turn_off_light,
        "cron",
        hour=end_time.hour,
        minute=end_time.minute,
        second=end_time.second,
        timezone=timezone,
        args=[device_id],
        id=f"off_{device_id}",
    )

    logger.info(f"Light cycle scheduled to start at {start_time} and end at {end_time}")


def turn_on_light(device_id):
    topic = f"{device_id}/{SWITCH_LIGHT_ON_TOPIC}"
    mqtt_client.publish_message(topic, "on")
    logger.info(f"Light turned on for device: {device_id}")


def turn_off_light(device_id):
    topic = f"{device_id}/{SWITCH_LIGHT_OFF_TOPIC}"
    mqtt_client.publish_message(topic, "off")
    logger.info(f"Light turned off for device: {device_id}")
