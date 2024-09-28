from pydantic import BaseModel, Field
from typing import Optional
from utils.alerts import Type, Status, Topic, TOPIC_MESSAGES


class DBAlert(BaseModel):
    id: Optional[str] = Field(alias="_id")
    device_id: str
    type: Type
    status: Status
    topic: Topic

    class Config:
        allow_population_by_field_name: True


class Alert(DBAlert):
    message: str

    @classmethod
    def from_db_alert(cls, db_alert: DBAlert) -> "Alert":
        return cls(
            **db_alert.dict(by_alias=True), message=TOPIC_MESSAGES[db_alert.topic]
        )


class AlertUpdate(DBAlert):
    id: str
    device_id: Optional[str] = None
    type: Optional[Type] = None
    status: Optional[Status] = None
    topic: Optional[Topic] = None

    class Config:
        use_enum_values = True
