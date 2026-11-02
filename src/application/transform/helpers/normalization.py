from typing import Any

import pendulum
from pyflink.datastream.functions import MapFunction

from src.config.settings import AppSettings
from src.models.normalized.transaction import NormalizedTransaction
from src.models.source.transaction import Transaction
from src.utils.json_schema_utils import JsonSchemaUtils

_NORMALIZED_CATEGORIES = {
    "segment",
    "transaction_type",
    "direction",
    "device_type",
    "status",
}

class NormalizeTransaction(MapFunction):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def map(self, value: Any) -> dict[str, Any]:
        values = dict(JsonSchemaUtils.data_mapping(value, Transaction))

        for field_name, field_value in values.items():
            if not isinstance(field_value, str):
                continue

            field_value = field_value.strip()
            if field_name in _NORMALIZED_CATEGORIES:
                field_value = field_value.lower()
            elif field_name == "currency":
                field_value = field_value.upper()
            values[field_name] = field_value

        transaction = Transaction.model_validate(values)
        transaction_values = transaction.model_dump()
        event_timestamp = pendulum.parse(
            transaction.event_timestamp,
            tz=self.settings.pipeline.tz,
        )

        transaction_values.update(
            event_timestamp=event_timestamp.naive(),
            latitude=float(transaction.latitude),
            longitude=float(transaction.longitude),
        )
        normalized = NormalizedTransaction(
            **transaction_values,
        )
        return normalized.model_dump()
