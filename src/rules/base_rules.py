from copy import deepcopy

from src.models.score_policy import ScorePolicy
from src.config.rules import FraudRule
from src.config.settings import AppSettings
from src.models.enums import FraudType, ThresholdLevel
from src.models.threshold import FraudThreshold, ThresholdResult


class BaseRules:

    def __init__(
        self,
        settings: AppSettings,
        fraud_type: FraudType,
        **key_select: str,
    ):
        self.score_policy: ScorePolicy = settings.score_policy
        self.rule: FraudRule = getattr(settings.rules, fraud_type.value)
        self.key_select = key_select


    def _calculate_multiplier(self, key_select: dict[str, str]) -> float:
        multiplier = 1.0
        for category, selected_value in key_select.items():
            mapping = self.rule.factors.get(category)
            if mapping is None:
                raise ValueError(f"Unknown factor category: {category}")

            factor = mapping.get(selected_value)
            if factor is None:
                raise ValueError(
                    f"Unknown value '{selected_value}' for factor '{category}'"
                )
            multiplier *= factor

        return multiplier

    def _calculate_threshold(self, key_select: dict[str, str]) -> FraudThreshold:
        threshold = deepcopy(self.rule.threshold)
        multiplier = self._calculate_multiplier(key_select)

        for level in (threshold.low, threshold.medium, threshold.high):
            level.value *= multiplier

        return threshold

    @staticmethod
    def _calculate_score(value: float, threshold: FraudThreshold) -> tuple[int, ThresholdLevel]:
        if value >= threshold.high.value:
            return threshold.high.score, ThresholdLevel.HIGH
        if value >= threshold.medium.value:
            return threshold.medium.score, ThresholdLevel.MEDIUM
        if value >= threshold.low.value:
            return threshold.low.score, ThresholdLevel.LOW
        return 0, ThresholdLevel.NONE

    def get_score(self, value: float, **key_select: str) -> int:
        selected_factors = key_select or self.key_select
        threshold = self._calculate_threshold(selected_factors)
        return self._calculate_score(value, threshold)

    def get_result(self, value: float, **key_select: str) -> ThresholdResult:
        selected_factors = key_select or self.key_select
        threshold = self._calculate_threshold(selected_factors)
        score = self._calculate_score(value, threshold)

        return ThresholdResult(
            rule_type="",
            agg_type=self.rule.aggregation,
            value=value,
            score=score[0],
            level=score[1]
        )


if __name__ == "__main__":
    rules = BaseRules(
        settings=AppSettings(),
        fraud_type=FraudType.AMOUNT,
        segment="retail",
        transaction_type="payment",
        direction="out",
    )

    print(rules.get_score(100.0))
    print(rules.key_select)
    print(rules.rule)