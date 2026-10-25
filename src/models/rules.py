from pydantic import BaseModel
from src.models.enums import FraudStatus


class FraudResult(BaseModel):
    score: int
    threshold: float
    fraud_status: FraudStatus