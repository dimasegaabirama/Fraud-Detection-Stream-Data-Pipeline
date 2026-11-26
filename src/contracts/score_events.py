from typing import Any, Annotated
from pydantic import BaseModel, Field, model_validator
from src.common.format import TIMESTAMP_FORMAT

from src.models.enums import FraudAction
from src.models.rules import RuleResults


class FraudResult(BaseModel):
    user_id: str
    rule_results: RuleResults
    final_score: float
    action: FraudAction
    event_timestamp: str
    detected_at: str


if __name__ == "__main__":
    pass