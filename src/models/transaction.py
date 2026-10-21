from typing_extensions import Optional
from pydantic import BaseModel, field_validator, model_validator, Field

from src.models.enums import (
    DeviceType,
    SegmentType,
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
    sender_account: Optional[str] = None
    receiver_account: Optional[str] = None
    merchant_id: Optional[str] = None
    ip_address: str
    device_id: str
    device_type: str
    latitude: float
    longitude: float
    status: str
    event_timestamp: str

    @field_validator(
        "status", 
        "transaction_type", 
        "direction", 
        "device_type", 
        "segment", 
        mode="before"
    )
    @classmethod
    def normalize_enum_values(cls, v: str) -> str:
        return v.upper()

    @model_validator(mode="after")
    def validate_enum_values(self):
        TransactionStatus(self.status)
        TransactionType(self.transaction_type)
        TransactionDirection(self.direction)
        DeviceType(self.device_type)
        SegmentType(self.segment)
        
        return self

if __name__ == "__main__":
    pass
