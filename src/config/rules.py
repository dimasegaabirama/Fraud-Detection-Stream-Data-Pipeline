from typing_extensions import Optional, List, Dict
from pathlib import Path

from pydantic import BaseModel, model_validator

from models.enums import Aggregation
from src.models.threshold import FraudThreshold


class FraudRule(BaseModel):
    enabled: bool = True
    aggregation: Aggregation
    group_key: List[str]
    agg_fields: List[str]
    window_minutes: Optional[int] = None
    threshold: FraudThreshold
    factors: Dict[str, Dict[str, float]] = {}

    @model_validator(mode="before")
    @classmethod
    def verify_aggregation(cls, values):
        aggregation = values.get("aggregation").upper()
        values["aggregation"] = Aggregation(aggregation)
        return values


class RulesSettings(BaseModel):
    amount: FraudRule
    device: FraudRule
    ip: FraudRule
    device: FraudRule
    speed: FraudRule
    velocity: FraudRule


if __name__ == "__main__":
    pass
