from typing import Any
from pydantic import BaseModel, Field, model_validator
from src.common.format import TIMESTAMP_FORMAT

from src.models.enums import (
    ThresholdLevelType,
    FraudType,
    RulesAction
)

class FactFraudEvaluations(BaseModel):
    transaction_id: str
    user_id: str
    fraud_type: FraudType
    level: ThresholdLevelType
    base_score: int = Field(ge=0)
    factor: float = Field(ge=0)
    contribution_score: int = Field(ge=0)

    observed_value: float = Field(ge=0)
    threshold_value: float = Field(ge=0)
    evidence: dict[str, Any]

    event_time: str
    detected_at: str
    day: int = Field(gt=0, lt=32)
    month: int = Field(gt=0, lt=13)
    year: int = Field(ge=2000, le=9999)


class FraudAlerts(BaseModel):
    alert_id: str | None = None
    user_id: str

    rule_levels: dict[str, ThresholdLevelType]
    final_score: int = Field(ge=0)
    action: RulesAction
    event_time: str
    detected_at: str

    @model_validator(mode="before")
    @classmethod
    def build_alert_id(cls, data):
        import hashlib

        if not isinstance(data, dict):
            return data

        data = data.copy()

        if not data.get("alert_id"):
            raw = "\x1f".join((
                data["user_id"],
                data["event_time"]
            ))

            data["alert_id"] = (
                "alt_" + hashlib.blake2b(
                    raw.encode("utf-8"),
                    digest_size=16
                ).hexdigest()
            )

        return data

if __name__ == "__main__":
    alerts = FraudAlerts(
        user_id="001", 
        rule_levels={"R1": "low"}, 
        final_score=100, 
        action="block", 
        event_time="2024-01-01 19:00:00",
        detected_at="2024-01-01 19:00:00"
    )

    print(alerts)