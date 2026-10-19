from models.enums import Aggregation, TransactionDirection, TransactionType
from config.rules import RuleConfig
from src.models.threshold import FraudThreshold, LevelThreshold
from src.rules.base_rules import BaseRules


class DeviceRules(BaseRules):
    """
    A class to represent the device rules for fraud detection.
    Attributes:
        CONFIG (RuleConfig): Configuration for the device rules.
        FACTORS (dict): Factors affecting the scoring based on direction and transaction type.
    """

    CONFIG: RuleConfig = RuleConfig(
        enabled=True,
        threshold=FraudThreshold(
            low=LevelThreshold(value=1.0, score=10),
            medium=LevelThreshold(value=3.0, score=50),
            high=LevelThreshold(value=5.0, score=80),
        ),
        aggregation=Aggregation.COUNT,
        group_key=["user_id", "device_id", "direction", "transaction_type"],
        agg_field="device_id",
        window_minutes=60,
    )

    FACTORS = {
        "direction": {
            TransactionDirection.CREDIT: 1.0,
            TransactionDirection.DEBIT: 1.2,
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
    pass
