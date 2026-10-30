from typing import Any

from pyflink.datastream import KeyedProcessFunction, StreamExecutionEnvironment
from pyflink.datastream.data_stream import DataStream

from src.config.settings import AppSettings
from transform.normalize_transaction import (
    NormalizeTransaction,
)

from src.utils.flink_utils import FlinkUtils
from src.models.sink import TransactionFraudAlert


class TransactionFraudAlertTransformer(KeyedProcessFunction):
    def open(self, runtime_context):
        pass

    def process_element(self, value, ctx):
        pass

class TransactionFraudAlert:

    OUTPUT_TYPE = FlinkUtils.build_row_type_info(TransactionFraudAlert)

    @classmethod
    def transform(cls, data_stream: DataStream[Any], settings: AppSettings, env: StreamExecutionEnvironment) -> DataStream[Any]:

        return data_stream.map(
            func=NormalizeTransaction(settings)
        ).key_by(
            lambda x: (x["user_id"], x["transaction_id"])
        ).process(
            func=TransactionFraudAlertTransformer(),
            output_type=cls.OUTPUT_TYPE,
        )