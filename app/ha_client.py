import os
import requests

from logger import logger


HA_BASE_URL = os.getenv("HA_URL")

HA_TOPIC = {
    "temperature": "",
    "ph": "",
    "ec": "",
    "humidity": "",
    "room_temperature": "",
    "floater": "-Py0_tP3ybDyV-O2IOiIQNDpe"
}

HEADERS = {
    "Content-Type": "application/json"
}
def send_to_ha(device_id: str, sensor: str, reading: float):
    try:
        # Construct the URL
        url = HA_BASE_URL + HA_TOPIC[sensor]

        # Log the request information
        logger.info(f"sending request for topic: {sensor} to HA at url: {url}")

        # Prepare the payload
        payload = {
            "reading": reading
        }

        # Send the POST request
        response = requests.post(url, json=payload, headers=HEADERS)

        # Log the response status
        logger.info(f"Received response status: {response.status_code}")
        if response.status_code != 200:
            logger.error(f"Error response: {response.text}")

    except Exception as e:
        logger.error(f"Something went wrong when sending to HA: {str(e)}")