from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from src.models.enums import (
    DeviceType,
    FraudStatus,
    SegmentType,
    TransactionDirection,
    TransactionType,
)


class TransactionFraudAlert(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    event_timestamp: datetime
    segment: SegmentType
    transaction_type: TransactionType
    direction: TransactionDirection
    amount: Decimal = Field(
        gt=Decimal("0.00"),
        json_schema_extra={"format": "decimal"},
    )
    currency: str = Field(min_length=3, max_length=3)
    device_type: DeviceType
    ip_address: str
    fraud_status: FraudStatus
    score: int = Field(ge=0)
    triggered_rules: str = Field(
        description="JSON-encoded array of rule names, for example [\"amount\", \"velocity\"]."
    )
