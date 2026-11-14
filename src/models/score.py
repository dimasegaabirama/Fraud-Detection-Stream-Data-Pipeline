from pydantic import BaseModel
from src.models.enums import (
    FraudType, 
    ThresholdLevelType, 
    RulesAction
)

class ScoreResult(BaseModel):
    type: FraudType
    evidence: dict[str, str]
    observed_value: float = 0.0
    threshold_value: float = 0.0
    base_score: int = 0.0
    factor: float = 1.0
    final_score: int = 0.0
    level: ThresholdLevelType
    action: RulesAction