from pydantic import BaseModel, model_validator


class ThresholdScore(BaseModel):
    value: float = 0.0
    score: int = 0

class ThresholdLevelScore(BaseModel):
    low: ThresholdScore
    medium: ThresholdScore
    high: ThresholdScore

    @model_validator(mode="after")
    def _validate_order(self):
        if not (self.low.value < self.medium.value < self.high.value):
            raise ValueError("Threshold values must be ascending: low < medium < high.")
        if not (self.low.score < self.medium.score < self.high.score):
            raise ValueError("Score values must be ascending: low < medium < high.")
        return self
