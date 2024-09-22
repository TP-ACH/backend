from pydantic import BaseModel
from typing import List, Optional
from utils.alerts import Type, Status

class Alert(BaseModel):
    type: Type
    status: Status
    message: str