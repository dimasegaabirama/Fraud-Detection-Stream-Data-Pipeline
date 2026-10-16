from src.domain.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class VelocityRules(BaseRules):
    VELOCITY_RULES = FraudThreshold(
        low=LevelThreshold(value=5.0, score=10),
        medium=LevelThreshold(value=10.0, score=50),
        high=LevelThreshold(value=20.0, score=80),
    )

    SEGMENT_FACTOR = {
        Segment.BUSINESS: 2.0,
        Segment.RETAIL: 1.3,
        Segment.INDIVIDUAL: 1.0,
    }

    TRANSACTION_TYPE_FACTOR = {
        TransactionType.CASHOUT: 0.6,
        TransactionType.WITHDRAWAL: 0.6,
        TransactionType.TRANSFER: 0.8,
        TransactionType.REFUND: 1.0,
        TransactionType.PAYMENT: 1.5,
        TransactionType.TOP_UP: 1.5,
    }

    DIRECTION_FACTOR = {
        Direction.CREDIT: 1.2,
        Direction.DEBIT: 1.0,
    }

    def get_thresholds(
        self, segment: Segment, direction: Direction, transaction_type: TransactionType
    ) -> FraudThreshold:
        base_threshold = self.VELOCITY_RULES

        direction_factor = self.DIRECTION_FACTOR.get(direction, 1.0)
        segment_factor = self.SEGMENT_FACTOR.get(segment, 1.0)
        transaction_type_factor = self.TRANSACTION_TYPE_FACTOR.get(transaction_type, 1.0)

        adjusted_low = (
            base_threshold.low.value * direction_factor * segment_factor * transaction_type_factor
        )
        adjusted_medium = (
            base_threshold.medium.value
            * direction_factor
            * segment_factor
            * transaction_type_factor
        )
        adjusted_high = (
            base_threshold.high.value * direction_factor * segment_factor * transaction_type_factor
        )

        return FraudThreshold(
            low=LevelThreshold(value=adjusted_low, score=base_threshold.low.score),
            medium=LevelThreshold(value=adjusted_medium, score=base_threshold.medium.score),
            high=LevelThreshold(value=adjusted_high, score=base_threshold.high.score),
        )
