from pydantic import BaseModel, model_validator
from src.domain.enums import SegmentLevel, StatusLevel, DirectionLevel

class Threshold(BaseModel):
    threshold: float = 0.0
    score: int = 0

class FraudThreshold(BaseModel):
    low: Threshold
    medium: Threshold
    high: Threshold


    @model_validator(mode='before')
    @classmethod
    def check_threshold_hierarchy(cls, values):
        if not (values['low'].threshold < values['medium'].threshold < values['high'].threshold):
            raise ValueError("Threshold values must be in ascending order: low < medium < high.")
        return values

    @model_validator(mode='before')
    @classmethod
    def check_score_hierarchy(cls, values):
        if not (values['low'].score < values['medium'].score < values['high'].score):
            raise ValueError("Score values must be in ascending order: low < medium < high.")
        return values

class FraudResult(BaseModel):
    user_id: str
    segment: SegmentLevel
    direction: DirectionLevel
    score: int
    status: StatusLevel