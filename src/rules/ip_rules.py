from src.rules.base_rules import BaseRules
from src.domain.enums import DirectionLevel, SegmentLevel
from src.models.rules import IPAddressRulesConfig


class IPRules(BaseRules):
    def segment_business_threshold(self) -> IPAddressRulesConfig:
        s = SegmentLevel.BUSINESS

        return IPAddressRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(10, 10.0),
                    medium=(15, 50.0),
                    high=(20, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(8, 15.0),
                    medium=(12, 60.0),
                    high=(16, 90.0),
                ),
            ]
        )

    def segment_retail_threshold(self) -> IPAddressRulesConfig:
        s = SegmentLevel.RETAIL

        return IPAddressRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(5, 10.0),
                    medium=(7, 50.0),
                    high=(10, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(4, 15.0),
                    medium=(6, 60.0),
                    high=(8, 90.0),
                ),
            ]
        )

    def segment_individual_threshold(self) -> IPAddressRulesConfig:
        s = SegmentLevel.INDIVIDUAL

        return IPAddressRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(3, 10.0),
                    medium=(4, 50.0),
                    high=(6, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(2, 15.0),
                    medium=(3, 60.0),
                    high=(5, 90.0),
                ),
            ]
        )