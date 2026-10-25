from pydantic import BaseModel, model_validator
from src.models.enums import FraudType, ThresholdLevel

class ThresholdResult(BaseModel):
    type: FraudType
    value: float = 0.0
    score: int = 0
    level: ThresholdLevel 


class ThresholdLevelScore(BaseModel):
    value: float = 0.0
    score: int = 0


class FraudThreshold(BaseModel):
    low: ThresholdLevelScore
    medium: ThresholdLevelScore
    high: ThresholdLevelScore

    @model_validator(mode="after")
    def validate_order(self):
        if not (self.low.value < self.medium.value < self.high.value):
            raise ValueError("Threshold values must be ascending: low < medium < high.")
        if not (self.low.score < self.medium.score < self.high.score):
            raise ValueError("Score values must be ascending: low < medium < high.")
        return self