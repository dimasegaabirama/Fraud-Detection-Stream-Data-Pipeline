from pydantic import BaseModel, model_validator

from src.domain.enums import Direction, Segment, TransactionStatus


class LevelThreshold(BaseModel):
    value: float = 0.0
    score: int = 0


class FraudThreshold(BaseModel):
    low: LevelThreshold
    medium: LevelThreshold
    high: LevelThreshold

    @model_validator(mode="after")
    def check_hierarchy(self):
        if not (self.low.value < self.medium.value < self.high.value):
            raise ValueError("Threshold values must be ascending: low < medium < high.")
        if not (self.low.score < self.medium.score < self.high.score):
            raise ValueError("Score values must be ascending: low < medium < high.")
        return self


class FraudResult(BaseModel):
    user_id: str
    segment: Segment
    direction: Direction
    score: int
    status: TransactionStatus
