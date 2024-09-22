from pydantic import BaseModel, Field
from typing import Optional
from utils.alerts import Type, Status

class Alert(BaseModel):
    id: Optional[str] = Field(alias="_id")
    device_id: str
    type: Type
    status: Status
    message: str
    
    class Config:
        allow_population_by_field_name: True
        
class AlertUpdate(Alert):
    id: str
    device_id: Optional[str] = None
    type: Optional[Type] = None
    status: Optional[Status] = None
    message: Optional[str] = None
    
    class Config:
        use_enum_values = True