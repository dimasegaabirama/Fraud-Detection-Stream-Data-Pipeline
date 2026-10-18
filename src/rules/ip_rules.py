from src.domain.enums import Aggregation, Segment, TransactionType
from src.models.rules import RuleConfig
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class IPRules(BaseRules):
    """
    A class to represent the IP rules for fraud detection.
    Attributes:
        CONFIG (RuleConfig): Configuration for the IP rules.
        FACTORS (dict): Factors affecting the scoring based on segment and transaction type.
    """

    CONFIG: RuleConfig = RuleConfig(
        enabled=True,
        threshold=FraudThreshold(
            low=LevelThreshold(value=2.0, score=10),
            medium=LevelThreshold(value=4.0, score=50),
            high=LevelThreshold(value=6.0, score=80),
        ),
        aggregation=Aggregation.COUNT,
        group_key=["user_id", "ip_address", "segment", "transaction_type"],
        agg_field="ip_address",
        window_minutes=60,
    )

    FACTORS = {
        "segment": {
            Segment.BUSINESS: 2.0,
            Segment.RETAIL: 1.3,
            Segment.INDIVIDUAL: 1.0,
        },
        "transaction_type": {
            TransactionType.CASHOUT: 0.8,
            TransactionType.WITHDRAWAL: 0.8,
            TransactionType.TRANSFER: 0.9,
            TransactionType.PAYMENT: 1.0,
            TransactionType.TOP_UP: 1.1,
            TransactionType.REFUND: 1.1,
        },
    }


if __name__ == "__main__":
    pass
