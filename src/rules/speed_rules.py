from models.enums import Aggregation, Segment
from config.rules import RuleConfig
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class SpeedRules(BaseRules):
    """
    A class to represent the speed rules for fraud detection.
    """

    CONFIG: RuleConfig = RuleConfig(
        enabled=True,
        threshold=FraudThreshold(
            low=LevelThreshold(value=300.0, score=10),
            medium=LevelThreshold(value=600.0, score=50),
            high=LevelThreshold(value=900.0, score=80),
        ),
        aggregation=Aggregation.CUSTOM,
        group_key=["user_id", "segment"],
        agg_fields=["latitude", "longitude", "timestamp"],
        window_minutes=None,
    )

    FACTORS = {
        "segment": {
            Segment.BUSINESS: 1.2,
            Segment.RETAIL: 1.1,
            Segment.INDIVIDUAL: 1.0,
        }
    }
