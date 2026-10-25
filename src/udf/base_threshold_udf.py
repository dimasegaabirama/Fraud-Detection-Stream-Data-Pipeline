from collections.abc import Callable

from pyflink.table import ScalarFunction

from src.rules.base_rules import BaseRules


class BaseThresholdUDF(ScalarFunction):
    def __init__(self, rules_factory: Callable[[], BaseRules]):
        super().__init__()
        self.rules_factory = rules_factory
        self.rules: BaseRules | None = None

    def open(self, function_context):
        self.rules: BaseRules = self.rules_factory()

    def eval(
        self, segment: str, direction: str, transaction_type: str, value: float
    ) -> int:
        if self.rules is None:
            raise RuntimeError("BaseThresholdUDF has not been opened")
        return self.rules.get_score(
            value,
            segment=segment,
            direction=direction,
            transaction_type=transaction_type,
        )


if __name__ == "__main__":
    pass
