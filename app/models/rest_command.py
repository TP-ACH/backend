from pydantic import BaseModel, RootModel
from typing import Dict, Optional

class RestCommand(BaseModel):
    url: str
    method: str
    alias: Optional[str] = None

class RestCommandConfig(RootModel[Dict[str, RestCommand]]):
    pass