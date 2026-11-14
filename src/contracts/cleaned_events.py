from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator
from src.models.score import ScoreResult
from src.models.enums import (
    SegmentType, 
    DeviceType,
    TransactionDirection,
    TransactionStatus,
    TransactionType
)

from src.common.format import TIMESTAMP_FORMAT
from src.contracts.score_events import (
    BaseScoredEvents,
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
    processed_timestamp: str | None = None



    @field_validator(field="event_timestamp", mode="before")
    @classmethod
    def validate_timestamp(cls, value):
        try:
            datetime.strptime(value, TIMESTAMP_FORMAT)
        except Exception:
            raise ValueError(f"Format date on field 'event_timestamp' must be {TIMESTAMP_FORMAT}")
        return value


    def make_alert_id(self, score_result: ScoreResult) -> str:
        import hashlib

        raw = "\x1f".join((self.transaction_id, self.user_id, score_result.type))
        return "alt_" + hashlib.blake2b(raw.encode("utf-8"), digest_size=16).hexdigest()


    def to_scored_events(self, score_result: ScoreResult) -> BaseScoredEvents:
        return BaseScoredEvents(
            alert_id=self.make_alert_id(score_result),
            transaction_id=self.transaction_id,
            user_id=self.user_id,
            fraud_type=score_result.type,
            level=score_result.level,
            final_score=score_result.final_score,
            action=score_result.action,
            event_time=self.event_timestamp,
            detected_at=self.processed_timestamp,
        )

    
    def to_fact_fraud_evaluations(self, score_result: ScoreResult) -> FactFraudEvaluations:
        base_scored_events = self.to_scored_events(score_result).model_dump()
        event_timestamp = datetime.strptime(self.event_timestamp, TIMESTAMP_FORMAT)
        
        return FactFraudEvaluations(
            **base_scored_events,
            factor=score_result.factor,
            observed_value=score_result.observed_value,
            threshold_value=score_result.threshold_value,
            base_score=score_result.base_score,
            evidence=score_result.evidence,
            day=event_timestamp.day,
            month=event_timestamp.month,
            year=event_timestamp.year

        )

    def to_fraud_alerts(self, score_result: ScoreResult) -> FraudAlerts:
        base_scored_events = self.to_scored_events(score_result).model_dump()
        return FraudAlerts(**base_scored_events)