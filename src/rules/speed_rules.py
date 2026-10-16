from src.domain.enums import Segment
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class SpeedRules(BaseRules):
    SPEED_RULES = FraudThreshold(
        low=LevelThreshold(value=300.0, score=10),
        medium=LevelThreshold(value=600.0, score=50),
        high=LevelThreshold(value=900.0, score=80),
    )

    SEGMENT_FACTOR = {
        Segment.BUSINESS: 1.2,
        Segment.RETAIL: 1.1,
        Segment.INDIVIDUAL: 1.0,
    }

    def get_score(self, segment: Segment, value: float) -> float:
        threshold = self.get_thresholds(segment)

        if value >= threshold.high.value:
            return threshold.high.score
        elif value >= threshold.medium.value:
            return threshold.medium.score
        elif value >= threshold.low.value:
            return threshold.low.score
        else:
            return 0.0

    def get_thresholds(self, segment: Segment) -> FraudThreshold:
        base_threshold = self.SPEED_RULES
        segment_factor = self.SEGMENT_FACTOR.get(segment, 1.0)

        adjusted_low = base_threshold.low.value * segment_factor
        adjusted_medium = base_threshold.medium.value * segment_factor
        adjusted_high = base_threshold.high.value * segment_factor

        return FraudThreshold(
            low=LevelThreshold(value=adjusted_low, score=base_threshold.low.score),
            medium=LevelThreshold(value=adjusted_medium, score=base_threshold.medium.score),
            high=LevelThreshold(value=adjusted_high, score=base_threshold.high.score),
        )
