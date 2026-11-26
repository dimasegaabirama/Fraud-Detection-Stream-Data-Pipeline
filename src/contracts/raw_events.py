from decimal import Decimal

from pydantic import BaseModel, Field


class Transaction(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    currency: str
    segment: str
    transaction_type: str
    direction: str
    sender_account: str
    receiver_account: str
    merchant_id: str | None = None
    ip_address: str
    device_id: str
    device_type: str
    latitude: float
    longitude: float
    status: str
    event_timestamp: str