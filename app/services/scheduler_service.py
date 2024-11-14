import pytz
from datetime import datetime, timedelta
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.base import JobLookupError
from pymongo import MongoClient

from clients.mongodb_client import MONGODB_DB
from clients.mongodb_client import MONGODB_URI
from clients.mongodb_client import get_latest_sensor_readings
from controllers.mqtt_controller import mqtt_client
from controllers.alerts_controller import create_new_alert
from models.alert import DBAlert
from utils.alerts import Type, Status, Topic
from utils.consts import TIMEZONE
from utils.consts import TIME_THRESHOLD
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


def schedule_light_cycle(device_id, start_time, end_time, enabled=True):
    try:
        start_time = datetime.strptime(start_time, "%H:%M").time()
        end_time = datetime.strptime(end_time, "%H:%M").time()
    except ValueError:
        logger.error("Invalid time format. Please use HH:MM")
    try:
        scheduler.remove_job(f"on_{device_id}")
    except JobLookupError:
        logger.warning(f"No job by the id of on_{device_id} was found")
    try:
        scheduler.remove_job(f"off_{device_id}")
    except JobLookupError:
        logger.warning(f"No job by the id of off_{device_id} was found")

    if enabled:
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

        logger.info(
            f"Light cycle scheduled to start at {start_time} and end at {end_time}"
        )


def turn_on_light(device_id):
    topic = f"{device_id}/{SWITCH_LIGHT_ON_TOPIC}"
    mqtt_client.publish_message(topic, "on")
    logger.info(f"Light turned on for device: {device_id}")


def turn_off_light(device_id):
    topic = f"{device_id}/{SWITCH_LIGHT_OFF_TOPIC}"
    mqtt_client.publish_message(topic, "off")
    logger.info(f"Light turned off for device: {device_id}")


def sensors_heartbeat():
    scheduler.add_job(
        check_sensor_health,
        "interval",
        seconds=60,
        timezone=timezone,
        id="heartbeat",
        replace_existing=True,
    )


async def check_sensor_health():
    latest_data = await get_latest_sensor_readings()
    now = datetime.now(timezone)

    for device, sensors in latest_data.items():
        for sensor, readings in sensors.items():
            latest_reading = readings[0] if readings else None
            reading_time = timezone.localize(
                datetime.strptime(latest_reading["created_at"], "%Y-%m-%d %H:%M:%S")
            )
            if now - reading_time > timedelta(minutes=TIME_THRESHOLD):
                match sensor:
                    case "ph":
                        topic = Topic.PH_FAIL
                    case "temperature":
                        topic = Topic.TEMPERATURE_FAIL
                    case "humidity":
                        topic = Topic.HUMIDITY_FAIL
                    case "ec":
                        topic = Topic.EC_FAIL
                alert = {
                    "id": "",
                    "device_id": device,
                    "type": Type.ERROR,
                    "status": Status.OPEN,
                    "topic": topic,
                }
                await create_new_alert(DBAlert(**alert))
