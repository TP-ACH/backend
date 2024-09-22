from models.alert import Alert, AlertUpdate
from utils.alerts import Status
from utils.logger import logger
from clients.mongodb_client import read_alerts, insert_alert, update_alert

async def create_new_alert(alert: Alert):
    existing_alerts = await read_alerts(device_id = alert.device_id, type = alert.type, message=alert.message)
    
    for db_alert in existing_alerts:
        if db_alert.status in [Status.OPEN, Status.PENDING]:
            logger.info(f"Alert already exists with id {db_alert.id}. Skipping creation.")
            return db_alert
            
    return await insert_alert(alert)

async def update_alert_status(id, device_id=None, type=None, status=None, message=None):
    alert_update = AlertUpdate(
        id=id,
        device_id=device_id,
        type=type,
        status=status,
        message=message,
    )
    return await update_alert(alert_update)