from pydantic import BaseModel
from typing import List, Optional, Dict

class Trigger(BaseModel):
    platform: str
    allowed_methods: List[str]
    local_only: bool
    webhook_id: str

class Action(BaseModel):
    service: str
    enabled: bool
    data: Dict

class Automation(BaseModel):
    id: str
    alias: str
    description: str
    trigger: List[Trigger]
    condition: Optional[List[Dict]] = []
    action: List[Action]
    mode: str