from src.models.sink import TransactionDaily, TransactionFraudAlert
from src.models.source.transaction import Transaction

SOURCE_REGISTRY = {
    "kafka_source": Transaction,
}

SINK_REGISTRY = {
    "kafka_sink": TransactionFraudAlert,
    "hive_sink": TransactionDaily,
}

