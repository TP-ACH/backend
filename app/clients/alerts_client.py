from models.alert import Alert, DBAlert, AlertUpdate
from utils.alerts import Status, Type, Topic, TOPIC_MESSAGES
from utils.logger import logger
from clients.mongodb_client import read_alerts, insert_alert, update_alert


def get_alerts_with_message(
    device_id: str = None, type: Type = None, status: Status = None, topic: Topic = None
) -> list[Alert]:
    db_alerts = read_alerts(device_id, type, status, topic)
    return [Alert.from_db_alert(db_alert) for db_alert in db_alerts]


def create_new_alert(alert: DBAlert):
    if alert.status in [Status.OPEN, Status.PENDING]:
        existing_alerts = read_alerts(
            device_id=alert.device_id,
            type=alert.type,
            status=Status.OPEN,
            topic=alert.topic,
        ) or read_alerts(
            device_id=alert.device_id,
            type=alert.type,
            status=Status.PENDING,
            topic=alert.topic,
        )

    if existing_alerts:
        logger.info(
            f"Alert already exists with id {existing_alerts[0].id}. Skipping creation."
        )
        return existing_alerts[0]
    
    return Alert.from_db_alert(insert_alert(alert))


async def update_alert_status(id, device_id=None, type=None, status=None, topic=None):
    alert_update = AlertUpdate(
        id=id,
        device_id=device_id,
        type=type,
        status=status,
        topic=topic,
    )
    return await update_alert(alert_update)
