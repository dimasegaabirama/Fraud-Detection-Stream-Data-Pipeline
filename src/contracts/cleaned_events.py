from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator
from src.models.score import ScoreResult, ScoreAggregate
from src.models.enums import (
    SegmentType, 
    DeviceType,
    TransactionDirection,
    TransactionStatus,
    TransactionType,
    FraudType
)

from src.common.format import TIMESTAMP_FORMAT
from src.contracts.score_events import (
    FactFraudEvaluations,
    FraudAlerts
)

class CleanedTransaction(BaseModel):
    event_id: str
    transaction_id: str
    user_id: str
    amount: Decimal = Field(gt=Decimal("0.00"))
    currency: str = Field(min_length=3, max_length=3)
    segment: SegmentType
    transaction_type: TransactionType
    direction: TransactionDirection
    sender_account: str | None = None
    receiver_account: str | None = None
    merchant_id: str | None = None
    ip_address: str
    device_id: str
    device_type: DeviceType
    latitude: float
    longitude: float 
    status: TransactionStatus
    event_timestamp: str
    processed_timestamp: str

    @model_validator(mode="before")
    @classmethod
    def validate_timestamp(cls, value):
        timestamp_fields = ["event_timestamp", "processed_timestamp"]
        try:
            for field in timestamp_fields:
                datetime.strptime(value[field], TIMESTAMP_FORMAT)
        except Exception:
            raise ValueError(f"Format date on field 'event_timestamp' must be {TIMESTAMP_FORMAT}")
        
        return value

    def to_fact_fraud_evaluations(self, score_result: ScoreResult) -> FactFraudEvaluations:
        event_timestamp = datetime.strptime(self.event_timestamp, TIMESTAMP_FORMAT)

        return FactFraudEvaluations(
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            fraud_type=score_result.fraud_type,
            level=score_result.level,
            base_score=score_result.base_score,
            factor=score_result.factor,
            contribution_score=score_result.contribution_score,
            observed_value=score_result.observed_value,
            threshold_value=score_result.threshold_value,
            evidence=score_result.evidence,
            event_time=self.event_timestamp,
            detected_at=self.processed_timestamp,
            day=event_timestamp.day,
            month=event_timestamp.month,
            year=event_timestamp.year
        )

    def to_fraud_alerts(self, score_agg: ScoreAggregate) -> FraudAlerts:
        return FraudAlerts(
            user_id=self.user_id,
            final_score=score_agg.final_score,
            action=score_agg.action,
            event_time=self.event_timestamp,
            detected_at=self.processed_timestamp
        )