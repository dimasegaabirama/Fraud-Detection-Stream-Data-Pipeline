from abc import ABC
from copy import deepcopy

from src.config.rules import FraudRule
from src.config.settings import AppSettings
from src.models.enums import FraudType, ThresholdLevelType
from src.models.threshold import FraudThreshold, ThresholdResult


class BaseRules(ABC):
    def __init__(self, settings: AppSettings, fraud_type: FraudType):
        self.settings = settings.rules
        self.rule_config = getattr(self.settings, fraud_type.value)

    def _calculate_multiplier(self, key_values: dict[str, str]) -> float:
        multiplier = 1.0
        for category, selected_value in key_values.items():
            mapping = self.rule_config
            if mapping is None:
                raise ValueError(f"Unknown factor category: {category}")

            factor = mapping.get(selected_value)
            if factor is None:
                raise ValueError(f"Unknown value '{selected_value}' for factor '{category}'")
            multiplier *= factor

        return multiplier

    def _calculate_threshold(self, key_values: dict[str, str]) -> FraudThreshold:
        threshold = deepcopy(self.rule.threshold)
        multiplier = self._calculate_multiplier(key_values)

        for level in (threshold.low, threshold.medium, threshold.high):
            level.value *= multiplier

        return threshold

    @staticmethod
    def _calculate_score(
        value: float, threshold: FraudThreshold
    ) -> tuple[int, int, ThresholdLevelType]:
        if value >= threshold.high.value:
            return threshold.high.score, threshold.high.value, ThresholdLevelType.HIGH
        if value >= threshold.medium.value:
            return threshold.medium.score, threshold.medium.value, ThresholdLevelType.MEDIUM
        if value >= threshold.low.value:
            return threshold.low.score, threshold.low.value, ThresholdLevelType.LOW
        return 0, 0, ThresholdLevelType.NONE

    def get_score(self, value: float, **key_values: str) -> int:
        selected_factors = key_values or self.key_values
        threshold = self._calculate_threshold(selected_factors)
        return self._calculate_score(value, threshold)

    def get_result(self, value: float, **key_values: str) -> ThresholdResult:
        multiplier = self._calculate_multiplier(key_values)
        threshold = self._calculate_threshold(key_values)
        base_score, threshold_value, level = self._calculate_score(value, threshold)

        return ThresholdResult(
            type=self.fraud_type,
            level=level,
            threshold_value=threshold_value,
            base_score=base_score,
            factor=multiplier,
            final_score=int(base_score),
        )


if __name__ == "__main__":
    rules = BaseRules(
        settings=AppSettings(),
        fraud_type="amount",
        segment="retail",
        transaction_type="payment",
        direction="out",
    )

    print(rules.get_score(100.0))
    print(rules.key_select)
    print(rules.rule)
