from pydantic import BaseModel, model_validator, Field

from src.models.enums import (
    DeviceType,
    Segment,
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
    segment: str
    transaction_type: str
    direction: str
    sender_account: str | None = None
    receiver_account: str | None = None
    merchant_id: str | None = None
    ip_address: str
    device_id: str
    device_type: str
    latitude: float
    longitude: float
    status: str
    timestamp: str

    @model_validator(mode="after")
    def validate_enum_values(self):
        TransactionStatus(self.status.upper())
        TransactionType(self.transaction_type.upper())
        TransactionDirection(self.direction.upper())
        DeviceType(self.device_type.upper())
        Segment(self.segment.upper())
        
        return self

if __name__ == "__main__":
    txn = {
        "event_id": "evt_1",
        "transaction_id": "txn_1",
        "user_id": "user_1",
        "amount": 100.0,
        "currency": "USD",
        "segment": "retail",
        "transaction_type": "cashout",
        "direction": "credit",
        "sender_account": "sender_1",
        "receiver_account": "receiver_1",
        "merchant_id": "merchant_1",
        "ip_address": "192.168.1.1",
        "device_id": "device_1",
        "device_type": "web",
        "latitude": 0.0,
        "longitude": 0.0,
        "status": "success",
        "timestamp": "2023-04-01T00:00:00Z",
    }

    transaction = Transaction(**txn)
    print(transaction)
