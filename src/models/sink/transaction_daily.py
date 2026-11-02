from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)


class TransactionDaily(BaseModel):
    transaction_id: str
    user_id: str
    event_date: date
    event_timestamp: datetime
    segment: SegmentType
    transaction_type: TransactionType
    direction: TransactionDirection
    status: TransactionStatus
    sender_account: str | None = None
    receiver_account: str | None = None
    merchant_id: str | None = None
    currency: str = Field(
        min_length=3,
        max_length=3,
        description="Currency must be a valid 3-letter ISO code.",
    )
    amount: Decimal = Field(
        gt=Decimal("0.00"),
        description="Transaction amount must be greater than zero.",
    )
    device_id: str
    device_type: DeviceType
    ip_address: str
    latitude: float
    longitude: float
    year: int
    month: int = Field(ge=1, le=12)
    day: int = Field(ge=1, le=31)

if __name__ == "__main__":
    transaction_daily = TransactionDaily(
        transaction_id="txn_001",
        user_id="user_001",
        event_date=date(2026, 10, 28),
        event_timestamp=datetime(2026, 10, 28, 6, 36, 59),
        segment=SegmentType.RETAIL,
        transaction_type=TransactionType.PURCHASE,
        direction=TransactionDirection.OUTGOING,
        status=TransactionStatus.COMPLETED,
        sender_account="acc_001",
        receiver_account="acc_002",
        merchant_id="mrc_001",
        currency="USD",
        amount=Decimal("100.00"),
        device_id="dev_001",
        device_type=DeviceType.MOBILE,
        ip_address="",
        latitude=40.7128,
        longitude=-74.0060,
        year=2026,
        month=10,
        day=28,
    )