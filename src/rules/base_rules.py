from abc import ABC
from src.config.settings import AppSettings
from src.models.threshold import FraudThreshold, Threshold
from src.domain.enums import SegmentLevel, DirectionLevel
from src.models.rules import (
    BaseRule,
    BaseSegmentDirectionRule,
    BaseRulesConfig
)

class BaseRules(ABC):
    """Base class for all rules."""

    @classmethod
    def get_score(cls, segment: SegmentLevel, direction: DirectionLevel, value: float) -> FraudThreshold:

        # low=(2000.0, 10.0),
        # medium=(5000.0, 50.0),
        # high=(10000.0, 80.0),

        threshold = cls.get_thresholds(segment, direction)
        if value >= threshold.low.threshold:
            return threshold.low.score
        elif value >= threshold.medium.threshold:
            return threshold.medium.score
        elif value >= threshold.high.threshold:
            return threshold.high.score
        else:
            return 0.0
        

    @classmethod
    def get_thresholds(cls, segment: SegmentLevel, direction: DirectionLevel) -> FraudThreshold:
        segment_rules = {
            (SegmentLevel.BUSINESS, DirectionLevel.CREDIT): cls().segment_business_threshold().rules[0],
            (SegmentLevel.BUSINESS, DirectionLevel.DEBIT): cls().segment_business_threshold().rules[1],
            (SegmentLevel.RETAIL, DirectionLevel.CREDIT): cls().segment_retail_threshold().rules[0],
            (SegmentLevel.RETAIL, DirectionLevel.DEBIT): cls().segment_retail_threshold().rules[1],
            (SegmentLevel.INDIVIDUAL, DirectionLevel.CREDIT): cls().segment_individual_threshold().rules[0],
            (SegmentLevel.INDIVIDUAL, DirectionLevel.DEBIT): cls().segment_individual_threshold().rules[1]
        }

        if (segment, direction) not in segment_rules:
            raise ValueError(f"No rules found for segment {segment} and direction {direction}")

        return segment_rules.get((segment, direction)).rule.threshold

    def _rule(
        self,
        segment: SegmentLevel,
        direction: DirectionLevel,
        low: tuple,
        medium: tuple,
        high: tuple,
    ) -> BaseSegmentDirectionRule:

        return BaseSegmentDirectionRule(
            segment=segment,
            direction=direction,
            rule=BaseRule(
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
            ),
        )

    def segment_business_threshold(self) -> BaseRulesConfig:
        pass

    def segment_retail_threshold(self) -> BaseRulesConfig:
        pass

    def segment_individual_threshold(self) -> BaseRulesConfig:
        pass