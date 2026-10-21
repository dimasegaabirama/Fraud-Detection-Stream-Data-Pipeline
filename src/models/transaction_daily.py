import pendulum

from typing_extensions import Optional
from pydantic import BaseModel, model_validator, Field, field_validator
from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionStatus,
    TransactionType
)

class TransactionDaily(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    segment: str
    transaction_type: str
    direction: str
    sender_account: Optional[str] = None
    receiver_account: Optional[str] = None
    merchant_id: Optional[str] = None
    ip_address: str
    device_id: str
    device_type: str
    currency: str = Field(min_length=3, max_length=3, description="Currency must be a valid 3-letter ISO code.")
    amount: float = Field(gt=0, description="Transaction amount must be greater than zero.")
    latitude: float
    longitude: float
    status: str
    day: str
    month: str
    year: str
    event_timestamp: str

    @field_validator("event_timestamp", mode="after")
    @classmethod
    def validate_timestamp(cls, value):
        return pendulum.parse(value)


    @model_validator(mode="after")
    def validate_enum_values(self):
        TransactionStatus(self.status)
        TransactionType(self.transaction_type)
        TransactionDirection(self.direction)
        DeviceType(self.device_type)
        SegmentType(self.segment)
        
        return self


if __name__ == "__main__":

    from datetime import datetime

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

    txn_daily_dict = txn_daily.event_timestamp

    print(txn_daily_dict)