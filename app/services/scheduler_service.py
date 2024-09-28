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


def schedule_light_cycle(start_time, end_time):
    try:
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.strptime(end_time, "%H:%M").time()
    except ValueError:
        logger.error("Invalid time format. Please use HH:MM")
    scheduler.remove_all_jobs()

    scheduler.add_job(
        turn_on_light,
        "cron",
        hour=start_time.hour,
        minute=start_time.minute,
        second=start_time.second,
        timezone=timezone,
    )

    scheduler.add_job(
        turn_off_light,
        "cron",
        hour=end_time.hour,
        minute=end_time.minute,
        second=end_time.second,
        timezone=timezone,
    )

    logger.info(f"Light cycle scheduled to start at {start_time} and end at {end_time}")


def turn_on_light():
    mqtt_client.publish_message(SWITCH_LIGHT_ON_TOPIC, "on")
    logger.info("Light turned on")


def turn_off_light():
    mqtt_client.publish_message(SWITCH_LIGHT_OFF_TOPIC, "off")
    logger.info("Light turned off")
