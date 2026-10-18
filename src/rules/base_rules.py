from abc import ABC
from copy import deepcopy

from src.models.rules import RuleConfig
from src.models.threshold import FraudThreshold


class BaseRules(ABC):
    """
    An abstract base class for fraud detection rules.
    Attributes:
        CONFIG (RuleConfig): Configuration for the rule.
        FACTORS (dict): Factors affecting the scoring based on direction, segment, and transaction type.
    Methods:
        _calculate_threshold(factor_lookup: Dict[str, str]) -> FraudThreshold:
            Calculates the adjusted threshold based on the provided factors.
        _calculate_score(value: float) -> int:
            Calculates the score based on the provided value and the adjusted threshold.
    """

    CONFIG: "RuleConfig" = None
    FACTORS: dict[str, dict[str, float]] = None

    def __init__(self, factor_lookup: dict[str, str], value: float):
        if self.CONFIG is None or self.FACTORS is None:
            raise ValueError("CONFIG and FACTORS must be defined in the subclass.")

        self.threshold = self._calculate_threshold(factor_lookup)
        self.score = self._calculate_score(value)

    def _calculate_threshold(self, factor_lookup: dict[str, str]) -> FraudThreshold:
        threshold = deepcopy(self.CONFIG.threshold)

        multiplier = 1.0
        for key, mapping in self.FACTORS.items():
            multiplier *= mapping.get(factor_lookup[key], 1.0)

        for level in (threshold.low, threshold.medium, threshold.high):
            level.value *= multiplier
        return threshold

    def _calculate_score(self, value: float) -> int:
        t = self.threshold
        if value >= t.high.value:
            return t.high.score
        if value >= t.medium.value:
            return t.medium.score
        if value >= t.low.value:
            return t.low.score
        return 0


if __name__ == "__main__":
    rules = BaseRules().score
