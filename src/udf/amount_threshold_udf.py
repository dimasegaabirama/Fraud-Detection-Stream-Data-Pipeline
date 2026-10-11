
from typing_extensions import Dict, Tuple
from pyflink.table import ScalarFunction
from src.config.settings import AppSettings
from src.models.threshold import FraudThreshold
from src.domain.enums import DirectionLevel, SegmentLevel
from src.rules.amount_rules import AmountRules

class AmountThresholdUdf(ScalarFunction):
    def open(self, function_context):
        self.rules = AmountRules()

    def eval(self, segment: str, direction: str, value: float) -> FraudThreshold:
        return self.thresholds.get((SegmentLevel(segment), DirectionLevel(direction))).
