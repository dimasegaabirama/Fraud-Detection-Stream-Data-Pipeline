from typing import Any

from pyflink.datastream import KeyedProcessFunction, StreamExecutionEnvironment
from pyflink.datastream.data_stream import DataStream

from src.config.settings import AppSettings
from transform.normalize_transaction import (
    NormalizeTransaction,
)

from src.utils.flink_utils import FlinkUtils
from src.models.sink import TransactionDaily


    # event_id: str
    # transaction_id: str
    # user_id: str
    # segment: SegmentType
    # transaction_type: TransactionType
    # direction: TransactionDirection
    # sender_account: str | None = None
    # receiver_account: str | None = None
    # merchant_id: str | None = None
    # ip_address: str
    # device_id: str
    # device_type: DeviceType
    # currency: str = Field(min_length=3, max_length=3, description="Currency must be a valid 3-letter ISO code.")
    # amount: Decimal = Field(gt=Decimal("0.00"), description="Transaction amount must be greater than zero.")
    # latitude: Decimal
    # longitude: Decimal
    # status: TransactionStatus
    # day: str
    # month: str
    # year: str
    # event_timestamp: datetime

class TransactionDailyTransformer(KeyedProcessFunction):
    def open(self, runtime_context):
        pass

    def process_element(self, value, ctx):
        pass

class TransactionDaily:

    OUTPUT_TYPE = FlinkUtils.build_row_type_info(TransactionDaily)

    @classmethod
    def transform(cls, data_stream: DataStream[Any], settings: AppSettings, env: StreamExecutionEnvironment) -> DataStream[Any]:

        return data_stream.map(
            func=NormalizeTransaction(settings)
        ).key_by(
            lambda x: (x["user_id"], x["transaction_id"])
        ).process(
            func=TransactionDailyTransformer(),
            output_type=cls.OUTPUT_TYPE,
        )