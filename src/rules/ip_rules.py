from src.domain.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class IPRules(BaseRules):
    IP_RULES = FraudThreshold(
        low=LevelThreshold(value=2.0, score=10),
        medium=LevelThreshold(value=4.0, score=50),
        high=LevelThreshold(value=6.0, score=80),
    )

    SEGMENT_FACTOR = {
        Segment.BUSINESS: 2.0,
        Segment.RETAIL: 1.3,
        Segment.INDIVIDUAL: 1.0,
    }

    TRANSACTION_TYPE_FACTOR = {
        TransactionType.CASHOUT: 0.8,
        TransactionType.WITHDRAWAL: 0.8,
        TransactionType.TRANSFER: 0.9,
        TransactionType.PAYMENT: 1.0,
        TransactionType.TOP_UP: 1.1,
        TransactionType.REFUND: 1.1,
    }

    DIRECTION_FACTOR = {
        Direction.CREDIT: 1.0,
        Direction.DEBIT: 1.0,
    }

    def get_thresholds(
        self, segment: Segment, direction: Direction, transaction_type: TransactionType
    ) -> FraudThreshold:
        base_threshold = self.IP_RULES

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


if __name__ == "__main__":
    pass
