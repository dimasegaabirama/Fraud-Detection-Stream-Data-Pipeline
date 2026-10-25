from pydantic import BaseModel, Field

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
    event_timestamp: str

if __name__ == "__main__":
    pass
