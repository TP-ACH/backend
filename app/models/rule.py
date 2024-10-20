from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime


class Action(BaseModel):
    type: str
    dest: str


class Rule(BaseModel):
    bound: float
    compare: str
    time: int
    enabled: bool
    action: Action


class LightRule(BaseModel):
    start: str
    end: str

    @validator("start", "end")
    def validate_time(cls, value):
        try:
            datetime.strptime(value, "%H:%M")
        except ValueError:
            raise ValueError(f"Time '{value}' is not in the correct format '%H:%M'")
        return value


class RuleBySensor(BaseModel):
    sensor: str
    rules: List[Rule]


class DefaultRuleBySpecies(BaseModel):
    species: str
    rules_by_sensor: List[RuleBySensor]
    light_hours: LightRule


class RulesByDevice(BaseModel):
    device: str
    species: Optional[str] = None
    rules_by_sensor: Optional[List[RuleBySensor]] = None
    light_hours: Optional[LightRule] = None
