from pydantic import BaseModel
from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionType,
    FraudType,
    FraudStatus
)

class TransactionFraudAlert(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    segment: SegmentType
    transaction_type: TransactionType
    direction: TransactionDirection
    device_type: DeviceType
    ip_address: str
    speed: float | None = None
    fraud_type: FraudType
    fraud_status: FraudStatus
    fraud_value: float
    score: float


if __name__ == "__main__":
    pass
