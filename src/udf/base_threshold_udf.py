from pyflink.table import ScalarFunction

from models.enums import Direction, Segment, TransactionType
from src.models.threshold import FraudThreshold
from src.rules.base_rules import BaseRules


class BaseThresholdUDF(ScalarFunction):
    def __init__(self, rules_factory: BaseRules):
        super().__init__()
        self.rules_factory = rules_factory
        self.rules: BaseRules = None

    def open(self, function_context):
        self.rules: BaseRules = self.rules_factory()

    def eval(
        self, segment: str, direction: str, transaction_type: str, value: float
    ) -> FraudThreshold:
        return self.rules.get_score(
            Segment(segment), Direction(direction), TransactionType(transaction_type), value
        )


if __name__ == "__main__":
    pass
