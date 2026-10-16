from abc import ABC, abstractmethod

from src.domain.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold


class BaseRules(ABC):
    def get_score(
        self,
        segment: Segment,
        direction: Direction,
        transaction_type: TransactionType,
        value: float,
    ) -> float:
        threshold = self.get_thresholds(segment, direction, transaction_type)

        if value >= threshold.high.value:
            return threshold.high.score
        elif value >= threshold.medium.value:
            return threshold.medium.score
        elif value >= threshold.low.value:
            return threshold.low.score
        else:
            return 0.0

    @abstractmethod
    def get_thresholds(
        self, segment: Segment, direction: Direction, transaction_type: TransactionType
    ) -> FraudThreshold:
        raise NotImplementedError("Subclasses must implement this method.")


if __name__ == "__main__":
    rules = BaseRules

    print(rules.get_score(Segment.BUSINESS, Direction.CREDIT, TransactionType.WITHDRAWAL, 10000.0))
