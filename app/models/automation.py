from pydantic import BaseModel
from typing import List, Optional, Dict, Tuple

class Trigger(BaseModel):
    platform: str = "webhook"
    allowed_methods: List[str] = ["POST"]
    local_only: bool = True
    webhook_id: str

class Action(BaseModel):
    service: str
    data: Dict[str, str] = {
                "reading": "{{ trigger.json.reading | int }}"
            }

class Automation(BaseModel):
    id: str = None
    alias: str = None
    description: str
    trigger: List[Trigger] = []
    condition: Optional[List[Dict]] = []
    action: List[Action]
    mode: str = "single"
