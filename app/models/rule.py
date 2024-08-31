from pydantic import BaseModel
from typing import List

class Action(BaseModel):
    type: str
    dest: str

class Rule(BaseModel):
    bound: int
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