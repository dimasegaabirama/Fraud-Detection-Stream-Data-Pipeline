from pyflink.table import ScalarFunction
from src.models.threshold import FraudThreshold
from src.domain.enums import DirectionLevel, SegmentLevel
from src.rules.amount_rules import AmountRules

class AmountThresholdUdf(ScalarFunction):

    def get_score(self, segment: str, direction: str, value: float) -> FraudThreshold:
        segment_level = SegmentLevel(segment)
        direction_level = DirectionLevel(direction)
        return self.rules.get_thresholds(segment_level, direction_level)

    def open(self, function_context):
        self.rules = AmountRules()

    def eval(self, segment: str, direction: str, value: float) -> FraudThreshold:
        return self.rules.get_thresholds(SegmentLevel(segment), DirectionLevel(direction)).