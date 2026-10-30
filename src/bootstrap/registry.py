from models.source.transaction import Transaction
from src.models.sink import TransactionDaily, TransactionFraudAlert

SOURCE_REGISTRY = {
    "kafka_source": Transaction,
}

SINK_REGISTRY = {
    "kafka_sink": TransactionFraudAlert,
    "hive_sink": TransactionDaily
}

FRAUD_TRANSFORM_REGISTRY = {
    "velocity":
    "speed": 
    "ip_address":
    "device":
    "amount":
}

