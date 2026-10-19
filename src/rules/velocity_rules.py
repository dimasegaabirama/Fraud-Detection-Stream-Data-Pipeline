from models.enums import Aggregation, Segment, TransactionDirection, TransactionType
from config.rules import RuleConfig
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class VelocityRules(BaseRules):
    CONFIG: RuleConfig = RuleConfig(
        enabled=True,
        threshold=FraudThreshold(
            low=LevelThreshold(value=5.0, score=10),
            medium=LevelThreshold(value=10.0, score=50),
            high=LevelThreshold(value=20.0, score=80),
        ),
        aggregation=Aggregation.COUNT,
        group_key=["user_id", "segment", "direction", "transaction_type"],
        agg_fields=["transaction_id"],
        window_minutes=60,
    )

    FACTORS = {
        "segment": {
            Segment.BUSINESS: 2.0,
            Segment.RETAIL: 1.3,
            Segment.INDIVIDUAL: 1.0,
        },
        "transaction_type": {
            TransactionType.CASHOUT: 0.6,
            TransactionType.WITHDRAWAL: 0.6,
            TransactionType.TRANSFER: 0.8,
            TransactionType.REFUND: 1.0,
            TransactionType.PAYMENT: 1.5,
            TransactionType.TOP_UP: 1.5,
        },
        "direction": {
            TransactionDirection.CREDIT: 1.2,
            TransactionDirection.DEBIT: 1.0,
        },
    }
