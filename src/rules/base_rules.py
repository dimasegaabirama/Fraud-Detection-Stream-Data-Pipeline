from copy import deepcopy

from src.config.rules import FraudRule
from src.config.settings import AppSettings
from src.models.enums import FraudType
from src.models.threshold import FraudThreshold


class BaseRules:

    def __init__(
        self,
        settings: AppSettings,
        fraud_type: FraudType,
        **key_select: str,
    ):
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
    def _calculate_score(value: float, threshold: FraudThreshold) -> int:
        if value >= threshold.high.value:
            return threshold.high.score
        if value >= threshold.medium.value:
            return threshold.medium.score
        if value >= threshold.low.value:
            return threshold.low.score
        return 0

    def get_score(self, value: float, **key_select: str) -> int:
        selected_factors = key_select or self.key_select
        threshold = self._calculate_threshold(selected_factors)
        return self._calculate_score(value, threshold)

    def get_result(self, value: float, **key_select: str) -> dict[str, any]:
        selected_factors = key_select or self.key_select
        threshold = self._calculate_threshold(selected_factors)
        score = self._calculate_score(value, threshold)

        return {
            "value": value,
            "score": score,
            "threshold": threshold.dict(),
            "key_select": selected_factors,
        }


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