from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator
from src.models.enums import (
    SegmentType,
    DeviceType,
    TransactionDirection,
    TransactionStatus,
    TransactionType
)

from src.common.format import TIMESTAMP_FORMAT


class CleanedTransaction(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    currency: str = Field(min_length=3, max_length=3)
    segment: SegmentType
    transaction_type: TransactionType
    direction: TransactionDirection
    sender_account: str | None = None
    receiver_account: str | None = None
    merchant_id: str | None = None
    ip_address: str
    device_id: str
    device_type: DeviceType
    latitude: float
    longitude: float 
    status: TransactionStatus
    event_timestamp: str
    processed_timestamp: str

    @model_validator(mode="before")
    @classmethod
    def validate_timestamp(cls, value):
        timestamp_fields = ["event_timestamp", "processed_timestamp"]
        try:
            for field in timestamp_fields:
                datetime.strptime(value[field], TIMESTAMP_FORMAT)
        except Exception:
            raise ValueError(f"Format date on field 'event_timestamp' must be {TIMESTAMP_FORMAT}")
        
        return value