import pendulum

from pydantic import BaseModel, Field, field_validator
from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionStatus,
    TransactionType
)

from datetime import datetime

class TransactionDaily(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    segment: SegmentType
    transaction_type: TransactionType
    direction: TransactionDirection
    sender_account: str | None = None
    receiver_account: str | None = None
    merchant_id: str | None = None
    ip_address: str
    device_id: str
    device_type: DeviceType
    currency: str = Field(min_length=3, max_length=3, description="Currency must be a valid 3-letter ISO code.")
    amount: float = Field(gt=0, description="Transaction amount must be greater than zero.")
    latitude: float
    longitude: float
    status: TransactionStatus
    day: str
    month: str
    year: str
    event_timestamp: datetime

    @field_validator("event_timestamp", mode="after")
    @classmethod
    def validate_timestamp(cls, value):
        return pendulum.parse(value)


if __name__ == "__main__":

    txn_daily = TransactionDaily(
        event_id="evt_123",
        transaction_id="txn_456",
        user_id="user_789",
        segment=SegmentType.RETAIL.value,
        transaction_type=TransactionType.PAYMENT.value,
        direction=TransactionDirection.OUT.value,
        sender_account="acc_001",
        receiver_account="acc_002",
        merchant_id="merch_003",
        ip_address="192.168.1.1",
        device_id="dev_004",
        device_type=DeviceType.ANDROID.value,
        currency="USD",
        amount=100.0,
        latitude=40.7128,
        longitude=-74.0060,
        status=TransactionStatus.SUCCESS.value,
        day="01",
        month="01",
        year="2023",
        event_timestamp="2024-01-02 12:00:00"
    )

    txn_daily_dict = txn_daily.dict()

    print(txn_daily_dict)