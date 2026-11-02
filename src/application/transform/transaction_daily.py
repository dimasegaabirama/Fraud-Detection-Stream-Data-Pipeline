from __future__ import annotations

from typing import Any

import pendulum
from pyflink.common import Row
from pyflink.datastream.data_stream import DataStream
from pyflink.datastream.functions import MapFunction

from src.config.settings import AppSettings
from src.models.sink import TransactionDaily
from src.models.source import Transaction
from src.utils.flink_utils import FlinkUtils
from src.utils.json_schema_utils import JsonSchemaUtils


class _TransactionDailyMapper(MapFunction):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def map(self, value: Any) -> Row:
        transaction = Transaction.model_validate(
            JsonSchemaUtils.data_mapping(value=value, models=Transaction)
        )

        event_timestamp = pendulum.parse(
            transaction.event_timestamp,
            tz=self.settings.pipeline.tz,
        )

        daily_transaction = TransactionDaily(
            transaction_id=transaction.transaction_id,
            user_id=transaction.user_id,
            event_date=event_timestamp.date(),
            event_timestamp=event_timestamp.naive(),
            segment=transaction.segment,
            transaction_type=transaction.transaction_type,
            direction=transaction.direction,
            status=transaction.status,
            sender_account=transaction.sender_account,
            receiver_account=transaction.receiver_account,
            merchant_id=transaction.merchant_id,
            currency=transaction.currency,
            amount=transaction.amount,
            device_id=transaction.device_id,
            device_type=transaction.device_type,
            ip_address=transaction.ip_address,
            latitude=float(transaction.latitude),
            longitude=float(transaction.longitude),
            year=event_timestamp.year,
            month=event_timestamp.month,
            day=event_timestamp.day,
        )
        return Row(**daily_transaction.model_dump())


class TransactionDailyTransformer:
    OUTPUT_TYPE = FlinkUtils.build_row_type_info(TransactionDaily)
    
    @classmethod
    def transform(
        cls,
        data_stream: DataStream[Any],
        settings: AppSettings,
    ) -> DataStream[Any]:
        return data_stream.map(
            func=_TransactionDailyMapper(settings),
            output_type=cls.OUTPUT_TYPE,
        )
