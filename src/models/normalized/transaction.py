from datetime import datetime

from src.models.enums import (
    DeviceType,
    SegmentType,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
)
from src.models.source.transaction import Transaction


class NormalizedTransaction(Transaction):
    event_timestamp: datetime
    latitude: float
    longitude: float
    transaction_type: TransactionType
    direction: TransactionDirection
    status: TransactionStatus
    device_type: DeviceType
    segment: SegmentType
