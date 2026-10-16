
from pydantic import BaseModel

from src.domain.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold

# Base


class BaseRule(BaseModel):
    enabled: bool = True
    threshold: FraudThreshold


class BaseFraudRule(BaseModel):
    segment: Segment
    direction: Direction
    transaction_type: TransactionType
    rule: BaseRule


class BaseFraudRulesConfig(BaseModel):
    rules: list[BaseFraudRule]
