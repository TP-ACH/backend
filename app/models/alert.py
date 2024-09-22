from pydantic import BaseModel, Field
from typing import Optional
from utils.alerts import Type, Status
from bson import ObjectId

class Alert(BaseModel):
    id: Optional[str] = Field(alias="_id")
    type: Type
    status: Status
    message: str
    
    class Config:
        allow_population_by_field_name: True