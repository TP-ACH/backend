from pydantic import BaseModel
from typing import List, Optional

class Action(BaseModel):
    type: str
    dest: str

class Rule(BaseModel):
    bound: float
    compare:str
    time: int
    enabled: bool
    action: Action
 
class RuleBySensor(BaseModel):
    sensor: str
    rules: List[Rule]
    
class DefaultRuleBySpecies(BaseModel):
    species: str
    rules_by_sensor: List[RuleBySensor]
    light_hours: int
    
class RulesByDevice(BaseModel):
    device: str
    rules_by_sensor: Optional[List[RuleBySensor]] = None
    light_hours: Optional[int] = None