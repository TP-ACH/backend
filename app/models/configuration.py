from pydantic import BaseModel, RootModel
from typing import Dict, Optional


class RestCommandValue(BaseModel):
    url: str
    method: str

class RestCommandConfig(RootModel[Dict[str, RestCommandValue]]):
    pass

class Configuration(BaseModel):
    rest_command: Optional[RestCommandConfig] = None

