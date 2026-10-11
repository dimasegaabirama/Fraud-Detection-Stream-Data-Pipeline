from src.rules.base_rules import BaseRules
from src.domain.enums import DirectionLevel, SegmentLevel
from src.models.rules import SpeedRulesConfig


class SpeedRules(BaseRules):
    def segment_business_threshold(self) -> SpeedRulesConfig:
        s = SegmentLevel.BUSINESS

        return SpeedRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(120, 10.0),
                    medium=(250, 50.0),
                    high=(500, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(120, 15.0),
                    medium=(250, 60.0),
                    high=(500, 90.0),
                ),
            ]
        )

    def segment_retail_threshold(self) -> SpeedRulesConfig:
        s = SegmentLevel.RETAIL

        return SpeedRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(100, 10.0),
                    medium=(200, 50.0),
                    high=(400, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(100, 15.0),
                    medium=(200, 60.0),
                    high=(400, 90.0),
                ),
            ]
        )

    def segment_individual_threshold(self) -> SpeedRulesConfig:
        s = SegmentLevel.INDIVIDUAL

        return SpeedRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(80, 10.0),
                    medium=(150, 50.0),
                    high=(300, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(80, 15.0),
                    medium=(150, 60.0),
                    high=(300, 90.0),
                ),
            ]
        )