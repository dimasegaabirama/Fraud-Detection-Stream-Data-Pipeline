from pydantic import BaseModel, Field, model_validator

from src.models.enums import Aggregation, FraudType
from src.models.threshold import FraudThreshold


class FraudRule(BaseModel):
    enabled: bool = True
    aggregation: Aggregation
    group_key: list[str]
    agg_fields: list[str]
    timeout_ms: int | None = 30000
    threshold: FraudThreshold
    factors: dict[str, dict[str, float]] = Field(default_factory=dict)


class RulesSettings(BaseModel):
    amount: FraudRule
    device: FraudRule
    ip_address: FraudRule
    speed: FraudRule
    velocity: FraudRule

    @model_validator(mode="before")
    def validate_keys(cls, values):
        keys = values.keys()
        if set(keys) != set(FraudType.__members__.values()):
            raise ValueError(
                f"Invalid keys in rules settings. Expected keys: {list(FraudType.__members__.keys())}, \n"
                f"but got: {list(keys)}"
            )
        return values


if __name__ == "__main__":
    from src.config.settings import AppSettings

    settings = AppSettings()
    print(FraudType.__members__)
