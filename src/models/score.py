from typing import Any
from pydantic import BaseModel, model_validator, Field
from src.models.enums import (
    FraudType, 
    ThresholdLevelType, 
    RulesAction
)

class ScorePolicy(BaseModel):
    otp: int
    review: int
    block: int

    @model_validator(mode="after")
    def _validate_order(self):
        if not (self.otp < self.review < self.block):
            raise ValueError("Threshold values must be ascending: allow < otp < review < block.")
        return self

class ScoreResult(BaseModel):
    fraud_type: FraudType
    level: ThresholdLevelType

    evidence: dict[str, Any]

    observed_value: float = 0.0
    threshold_value: float = 0.0

    base_score: int = Field(default=0, ge=0)
    factor: float = Field(default=1.0, ge=0)
    contribution_score: int = Field(default=0, ge=0)

class ScoreAggregate(BaseModel):
    final_score: int = Field(ge=0)

    level: ThresholdLevelType
    action: RulesAction