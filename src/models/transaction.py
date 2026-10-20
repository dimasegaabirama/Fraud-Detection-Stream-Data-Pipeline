from pydantic import BaseModel, model_validator, Field

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
        SegmentType(self.segment.upper())
        
        return self

if __name__ == "__main__":
    from src.utils.flink_utils import FlinkUtils

    schemas = FlinkUtils.build_flink_schema(Transaction)
    for schema in schemas:
        print(schema)
