from typing import Any
from pydantic import BaseModel, Field
from src.models.enums import (
    FraudType,
    ThresholdLevelType
)


class RuleResult(BaseModel):
    fraud_type: FraudType
    level: ThresholdLevelType
    
    base_score: int = Field(ge=0)
    multiplier: float = Field(ge=0)
    contribution_score: int = Field(ge=0)

    observed_value: float = Field(ge=0)
    threshold_value: float = Field(ge=0)
    evidence: dict[str, Any]

RuleResults = dict[FraudType, RuleResult]