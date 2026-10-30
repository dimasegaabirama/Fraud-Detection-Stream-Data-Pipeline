from decimal import Decimal
from pydantic import BaseModel, Field

class Transaction(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    amount: Decimal = Field(gt=Decimal("0.00"), description="Amount must be a positive decimal value.")
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
    event_timestamp: str

if __name__ == "__main__":
    testes = Transaction(
        event_id="evt_001",
        transaction_id="txn_001",
        user_id="user_001",
        amount="100.00",
        currency="USD",
        segment="retail",
        transaction_type="purchase",
        direction="outgoing",
        sender_account="acc_001",
        receiver_account="acc_002",
        merchant_id="mrc_001",
        ip_address="192.168.1.1",
        device_id="dev_001",
        device_type="mobile",
        latitude=40.7128,
        longitude=-74.0060,
        status="completed",
        event_timestamp="2023-01-01T00:00:00Z"
    )

    print(testes.model_dump())
