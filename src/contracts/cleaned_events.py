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
    sender_account: str
    receiver_account: str
    merchant_id: str | None = None
    ip_address: str
    device_id: str
    device_type: DeviceType
    latitude: float
    longitude: float 
    status: TransactionStatus
    event_timestamp_ms: int
    processed_timestamp_ms: int