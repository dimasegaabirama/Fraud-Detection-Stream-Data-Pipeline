from abc import ABC
from copy import deepcopy

import math

from src.config.settings import AppSettings

from src.models.threshold import ThresholdLevelScore

from src.models.enums import FraudType, ThresholdLevelType
from src.models.rules import RuleResult


class BaseRules:

    def __init__(self, settings: AppSettings, fraud_type: FraudType):
        self.settings = settings.rules
        self.fraud_type = fraud_type
        self.rule_config = getattr(self.settings, fraud_type).model_dump()

    def _calculate_multiplier(self, key_values: dict[str, str]) -> float:
        multiplier = 1.0
        for category, selected_value in key_values.items():
            mapping = self.rule_config.get("factors").get(category)
            if mapping is None:
                raise KeyError(f"Unknown factor category: {category}")

            factor = mapping.get(selected_value, 1.0)
            multiplier *= factor

        return multiplier

    def _calculate_threshold(self, multiplier: float, key_values: dict[str, str]) -> ThresholdLevelScore:
        threshold = deepcopy(self.rule_config.get("threshold"))
        if threshold is None:
            raise KeyError(f"Threshold config is not found for fraud type : {self.fraud_type}")

        multiplier = self._calculate_multiplier(key_values)

        for level in (threshold["low"], threshold["medium"], threshold["high"]):
            level["value"] = round(level["value"] * multiplier, 2)

        return ThresholdLevelScore(**threshold)

    @staticmethod
    def _calculate_score(
        value: float, threshold: ThresholdLevelScore
    ) -> tuple[int, int, ThresholdLevelType]:
        if value >= threshold.high.value:
            return threshold.high.score, threshold.high.value, ThresholdLevelType.HIGH
        if value >= threshold.medium.value:
            return threshold.medium.score, threshold.medium.value, ThresholdLevelType.MEDIUM
        if value >= threshold.low.value:
            return threshold.low.score, threshold.low.value, ThresholdLevelType.LOW
        return 0, 0, ThresholdLevelType.NONE

    def get_result(self, value: float, **key_values: str) -> RuleResult:
        base_multiplier = 1.0
        base_score, _, _ = self._calculate_score(
            value=value,
            threshold=self._calculate_threshold(base_multiplier, key_values))

        multiplier = self._calculate_multiplier(key_values)
        threshold = self._calculate_threshold(multiplier, key_values)

        score, threshold_value, level = self._calculate_score(value, threshold)

        return RuleResult(
            fraud_type= self.fraud_type,
            level = level,
            base_score=base_score,
            multiplier=multiplier,
            contribution_score=score,
            observed_value=value,
            threshold_value=threshold_value,
            evidence=key_values
        )


if __name__ == "__main__":
    rules = BaseRules(
        settings=AppSettings(),
        fraud_type="device"
    )

    print(rules.get_result(4, direction = "in", transaction_type = "withdraw"))


