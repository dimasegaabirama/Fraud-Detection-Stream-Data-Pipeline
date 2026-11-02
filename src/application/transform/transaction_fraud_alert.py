from __future__ import annotations

from typing import Any

from pyflink.common import Row
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.data_stream import DataStream
from pyflink.datastream.functions import MapFunction

from src.config.settings import AppSettings
from src.models.sink import TransactionFraudAlert
from src.utils.flink_utils import FlinkUtils

FRAUD_RULES = {
    "amount": "Amount-based fraud detection",
    "device": "Device-based fraud detection",
    "ip_address": "IP address-based fraud detection",
    "speed": "Speed-based fraud detection",
    "velocity": "Velocity-based fraud detection"
}


class _TransactionFraudAlertMapper(MapFunction):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def map(self, value: Any) -> Row:
        # Implementation for mapping transaction to fraud alert
        pass

class TransactionFraudAlert:
    OUTPUT_TYPE = FlinkUtils.build_row_type_info(TransactionFraudAlert)

    @classmethod
    def transform(
        cls,
        data_stream: DataStream[Any],
        settings: AppSettings,
        env: StreamExecutionEnvironment,
    ) -> DataStream[Any]:

        return data_stream.key_by(
            lambda x: (x["user_id"], x["transaction_id"], x["direction"])
        ).process(
            func=TransactionFraudAlertTransformer(),
            output_type=cls.OUTPUT_TYPE,
        )