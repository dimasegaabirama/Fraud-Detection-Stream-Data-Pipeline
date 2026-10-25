from typing import Any

from pyflink.common import Duration
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.data_stream import DataStream

from src.bootstrap.init_schema import BootstrapInitializer
from src.config.settings import AppSettings
from src.functions.normalize_transaction import (
    NormalizeTransaction,
    TransactionTimestampAssigner,
)
from src.models.transaction import Transaction

from src.models.transaction_daily import TransactionDaily
from src.utils.flink_utils import FlinkUtils


class FraudDetectionJob:
    def __init__(self, settings: AppSettings, env: StreamExecutionEnvironment) -> None:
        self.settings = settings
        self.env = env

    def build_pipeline(self) -> DataStream[Any]:
        initializer = BootstrapInitializer(self.settings, self.env)
        sources = initializer.initialize_source({"kafka_source": Transaction})
        kafka_source = sources["kafka_source"]

        transactions = self.env.from_source(
            source=kafka_source,
            watermark_strategy=(
                WatermarkStrategy
                .for_bounded_out_of_orderness(Duration.of_seconds(5))
                .with_timestamp_assigner(TransactionTimestampAssigner(self.settings))
                .with_idleness(Duration.of_seconds(30))
            ),
            source_name="kafka_source",
        )

        return transactions.map(
            func=NormalizeTransaction(self.settings),
            output_type=FlinkUtils.build_row_type_info(TransactionDaily),
        )