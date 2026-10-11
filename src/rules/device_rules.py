from src.domain.enums import DirectionLevel, SegmentLevel
from src.models.rules import DeviceRule, DeviceRulesConfig, DeviceSegmentDirectionRule
from src.models.threshold import FraudThreshold, Threshold

from src.rules.base_rules import BaseRules

class DeviceRules(BaseRules):

    def segment_business_threshold(self) -> DeviceRulesConfig:
        s = SegmentLevel.BUSINESS
        return DeviceRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(10, 10.0),
                    medium=(11, 50.0),
                    high=(16, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(8, 15.0),
                    medium=(9, 60.0),
                    high=(13, 90.0),
                ),
            ]
        )

    def segment_retail_threshold(self) -> DeviceRulesConfig:
        s = SegmentLevel.RETAIL
        return DeviceRulesConfig(
            rules=[
                self._rule(
                    s,
                    DirectionLevel.CREDIT,
                    low=(6, 10.0),
                    medium=(7, 50.0),
                    high=(11, 80.0),
                ),
                self._rule(
                    s,
                    DirectionLevel.DEBIT,
                    low=(4, 15.0),
                    medium=(5, 60.0),
                    high=(8, 90.0),
                ),
            ]
        )

    def segment_individual_threshold(self) -> DeviceRulesConfig:
        s = SegmentLevel.INDIVIDUAL
        return DeviceRulesConfig(
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
                    high=(6, 90.0),
                ),
            ]
        )

if __name__ == "__main__":
    device_rules = DeviceRules()
    business_rules = device_rules.segment_business_threshold()
    retail_rules = device_rules.segment_retail_threshold()
    individual_rules = device_rules.segment_individual_threshold()

    print("Business Rules:", business_rules)
    print("\n")
    print("Retail Rules:", retail_rules)
    print("\n")
    print("Individual Rules:", individual_rules)