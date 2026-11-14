from pydantic import BaseModel, Field, field_validator

from pydantic import BaseModel, Field, field_validator

from src.models.enums import (
    ThresholdLevel,
    FraudType,
    RulesAction
)


class BaseScoredEvents(BaseModel):
    alert_id: str
    transaction_id: str = Field(min_length=1)
    user_id: str = Field(min_length=1)
    fraud_type: FraudType
    level: ThresholdLevel
    final_score: int = Field(ge=0)
    action: RulesAction
    event_time: str
    detected_at: str


class FactFraudEvaluations(BaseScoredEvents):
    factor: float = Field(ge=0)
    observed_value: float = Field(ge=0)
    threshold_value: float = Field(ge=0)
    base_score: int = Field(ge=0)
    evidence: dict[str, str]
    day: int = Field(gt=0, lt=32)
    month: int = Field(gt=0, lt=13)
    year: int = Field(ge=2000, le=9999)

    @field_validator("evidence", mode="before")
    @classmethod
    def standarize_evidence(cls, value):
        if isinstance(value, dict):
            return {str(k): str(val) for k, val in value.items()}
        return value
    

class FraudAlerts(BaseScoredEvents):
    pass
