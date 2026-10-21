import pendulum

from typing_extensions import Optional
from pydantic import BaseModel, model_validator, Field, field_validator
from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
    FraudType,
    FraudStatus
)

class TransactionFraud(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    segment: str
    transaction_type: str
    direction: str
    fraud_type: str
    fraud_status: str
    fraud_value: float
    score: float

    @field_validator(
        "fraud_type",
        "fraud_status",
        mode="before"
    )
    @classmethod
    def normalize_enum_values(cls, v: str) -> str:
        return v.upper()

    @model_validator(mode="after")
    def validate_enum_values(self):
        FraudType(self.fraud_type)
        FraudStatus(self.fraud_status)
        TransactionType(self.transaction_type)
        TransactionDirection(self.direction)
        SegmentType(self.segment)
        
        return self


