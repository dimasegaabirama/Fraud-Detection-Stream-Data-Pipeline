from src.domain.enums import Aggregation, Segment, TransactionDirection, TransactionType
from src.models.rules import RuleConfig
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class AmountRules(BaseRules):
    """
    A class to represent the amount rules for fraud detection.
    Attributes:
        CONFIG (RuleConfig): Configuration for the amount rules.
        FACTORS (dict): Factors affecting the scoring based on direction, segment, and transaction type.
    """

    CONFIG: RuleConfig = RuleConfig(
        enabled=True,
        threshold=FraudThreshold(
            low=LevelThreshold(value=1000.0, score=10),
            medium=LevelThreshold(value=5000.0, score=50),
            high=LevelThreshold(value=8000.0, score=80),
        ),
        aggregation=Aggregation.AVG,
        group_key=["user_id", "segment", "direction", "transaction_type"],
        agg_field="amount",
        window_minutes=60,
    )

    FACTORS = {
        "direction": {
            TransactionDirection.CREDIT: 1.0,
            TransactionDirection.DEBIT: 1.2,
        },
        "segment": {
            Segment.BUSINESS: 1.0,
            Segment.INDIVIDUAL: 1.0,
            Segment.RETAIL: 1.0,
        },
        "transaction_type": {
            TransactionType.CASHOUT: 1.0,
            TransactionType.PAYMENT: 1.0,
            TransactionType.REFUND: 0.8,
            TransactionType.TOP_UP: 1.0,
            TransactionType.TRANSFER: 1.0,
            TransactionType.WITHDRAWAL: 1.0,
        },
    }


if __name__ == "__main__":
    rules = AmountRules(
        factor_lookup={
            "direction": TransactionDirection.DEBIT,
            "segment": Segment.BUSINESS,
            "transaction_type": TransactionType.WITHDRAWAL,
        },
        value=10000.0,
    )
    print(rules.threshold)  # Expected output: 80
