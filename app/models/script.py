from pydantic import BaseModel, RootModel
from typing import Dict, Union, List, Optional


class LogData(BaseModel):
    name: str
    message: str

class ConditionTemplate(BaseModel):
    value_template: str

class Log(BaseModel):
    service: str = "logbook.log"
    data: LogData

class Condition(BaseModel):
    condition: str
    value_template: str

class RestCommand(BaseModel):
    service: str = "rest_command"
    target: Dict[str, str]

class Step(RootModel[Union[Log, Condition, RestCommand]]):
    pass

class Script(BaseModel):
    alias: Optional[str] = None
    sequence: List[Step]

class ScriptConfig(RootModel[Dict[str, Script]]):
    pass