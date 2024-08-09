from pydantic import BaseModel
from typing import Dict, List


class Attribute(BaseModel):
    upper: str
    lower: str

class Sensor(BaseModel):
    name: str
    unique_id: str
    state: str
    attributes: Attribute

class Template(BaseModel):
    sensor: List[Sensor]