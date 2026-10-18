from pathlib import Path

import yaml
from pydantic import BaseModel, model_validator

from src.domain.enums import Aggregation
from src.models.threshold import FraudThreshold


class FraudRule(BaseModel):
    enabled: bool = True
    aggregation: Aggregation
    group_key: list[str]
    agg_fields: list[str]
    window_minutes: int | None = None
    threshold: FraudThreshold
    factors: dict[str, dict[str, float]] = {}

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
