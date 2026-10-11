from src.rules.base_rules import BaseRules
from src.domain.enums import DirectionLevel, SegmentLevel
from src.models.rules import VelocityRulesConfig, VelocityRule, VelocitySegmentDirectionRule
from src.models.threshold import FraudThreshold, Threshold

class VelocityRules(BaseRules):
    
    def _rule(
        self,
        segment: SegmentLevel,
        direction: DirectionLevel,
        low: tuple,
        medium: tuple,
        high: tuple,
    ) -> VelocitySegmentDirectionRule:
        return VelocitySegmentDirectionRule(
            segment=segment,
            direction=direction,
            rule=VelocityRule(
                threshold=FraudThreshold(
                    low=Threshold(
                        threshold=low[0],
                        score=low[1],
                    ),
                    medium=Threshold(
                        threshold=medium[0],
                        score=medium[1],
                    ),
                    high=Threshold(
                        threshold=high[0],
                        score=high[1],
                    ),
                ),
            )
        )


    def segment_business_threshold(self) -> VelocityRulesConfig:
        s = SegmentLevel.BUSINESS

        return VelocityRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(14, 10.0),
                    medium=(15, 50.0),
                    high=(25, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(11, 15.0),
                    medium=(12, 60.0),
                    high=(20, 90.0),
                ),
            ]
        )

    def segment_retail_threshold(self) -> VelocityRulesConfig:
        s = SegmentLevel.RETAIL

        return VelocityRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(7, 10.0),
                    medium=(8, 50.0),
                    high=(12, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(5, 15.0),
                    medium=(6, 60.0),
                    high=(10, 90.0),
                ),
            ]
        )

    def segment_individual_threshold(self) -> VelocityRulesConfig:
        s = SegmentLevel.INDIVIDUAL

        return VelocityRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(4, 10.0),
                    medium=(5, 50.0),
                    high=(8, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(3, 15.0),
                    medium=(4, 60.0),
                    high=(7, 90.0),
                ),
            ]
        )