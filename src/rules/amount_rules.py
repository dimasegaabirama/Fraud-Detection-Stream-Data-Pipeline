from src.config.settings import AppSettings
from src.rules.base_rules import BaseRules
from src.domain.enums import DirectionLevel, SegmentLevel, ThresholdLevel
from src.models.rules import AmountRule, AmountRulesConfig, AmountSegmentDirectionRule
from src.models.threshold import FraudThreshold, Threshold



class AmountRules(BaseRules):

    def _rule(
        self, segment: SegmentLevel, direction: DirectionLevel, low: tuple, medium: tuple, high: tuple
    ) -> AmountSegmentDirectionRule:
        return AmountSegmentDirectionRule(
            segment=segment,
            direction=direction,
            rule=AmountRule(
                threshold=FraudThreshold(
                    low=Threshold(threshold=low[0], score=low[1]),
                    medium=Threshold(threshold=medium[0], score=medium[1]),
                    high=Threshold(threshold=high[0], score=high[1]),
                ),
            ),
        )

    def segment_business_threshold(self) -> AmountRulesConfig:
        s = SegmentLevel.BUSINESS
        return AmountRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(2000.0, 10.0),
                    medium=(5000.0, 50.0),
                    high=(10000.0, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(1500.0, 15.0),
                    medium=(4000.0, 60.0),
                    high=(8000.0, 90.0),
                ),
            ]
        )

    def segment_retail_threshold(self) -> AmountRulesConfig:
        s = SegmentLevel.RETAIL
        return AmountRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(1000.0, 10.0),
                    medium=(2500.0, 50.0),
                    high=(5000.0, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(750.0, 15.0),
                    medium=(2000.0, 60.0),
                    high=(4000.0, 90.0),
                ),
            ]
        )

    def segment_individual_threshold(self) -> AmountRulesConfig:
        s = SegmentLevel.INDIVIDUAL
        return AmountRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(500.0, 10.0),
                    medium=(1000.0, 50.0),
                    high=(2000.0, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(400.0, 15.0),
                    medium=(800.0, 60.0),
                    high=(1500.0, 90.0)
                )
            ]
        )

if __name__ == "__main__":

    rules = AmountRules()
    print(rules.get_thresholds(SegmentLevel.BUSINESS, DirectionLevel.DEBIT))