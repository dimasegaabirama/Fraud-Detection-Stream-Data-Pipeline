from src.domain.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class AvgAmountRules(BaseRules):
    AVG_AMOUNT_RULES = FraudThreshold(
        low=LevelThreshold(value=1000.0, score=10),
        medium=LevelThreshold(value=5000.0, score=50),
        high=LevelThreshold(value=8000.0, score=80),
    )

    DIRECTION_FACTOR = {
        Direction.CREDIT: 1.0,
        Direction.DEBIT: 1.2,
    }

    SEGMENT_FACTOR = {
        Segment.BUSINESS: 1.0,
        Segment.INDIVIDUAL: 1.0,
        Segment.RETAIL: 1.0,
    }

    TRANSACTION_TYPE_FACTOR = {
        TransactionType.CASHOUT: 1.0,
        TransactionType.PAYMENT: 1.0,
        TransactionType.REFUND: 0.8,
        TransactionType.TOP_UP: 1.0,
        TransactionType.TRANSFER: 1.0,
        TransactionType.WITHDRAWAL: 1.0,
    }

    def get_thresholds(
        self, segment: Segment, direction: Direction, transaction_type: TransactionType
    ) -> FraudThreshold:
        base_threshold = self.AVG_AMOUNT_RULES

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
    coba = AvgAmountRules()

    print(coba.get_score(Segment.BUSINESS, Direction.CREDIT, TransactionType.WITHDRAWAL, 900.0))
