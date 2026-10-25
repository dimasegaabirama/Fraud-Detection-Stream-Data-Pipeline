from pydantic import BaseModel, Field

from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)

class Transaction(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    amount: float = Field(gt=0, description="Transaction amount must be greater than zero.")
    currency: str = Field(min_length=3, max_length=3, description="Currency must be a valid 3-letter ISO code.")
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

if __name__ == "__main__":
    pass
