import pendulum
from decimal import Decimal
from pyflink.common.watermark_strategy import TimestampAssigner
from pyflink.datastream.functions import MapFunction

from src.config.settings import AppSettings
from src.models.source import Transaction

class NormalizeTransaction(MapFunction):
    def __init__(self, settings: AppSettings):
        self.settings = settings

    def map(self, value: dict) -> dict:
        transaction = Transaction(**value).model_dump()

        for key, value in transaction.items():
            if key == "event_timestamp":
                datetime = pendulum.parse(value, tz=self.settings.pipeline.tz)
                transaction[key] = datetime
            elif isinstance(value, str):
                transaction[key] = value.strip().lower() if value else None
            elif isinstance(value, (int, float)):
                transaction[key] = Decimal(str(value))

        transaction["day"] = datetime.day
        transaction["month"] = datetime.month
        transaction["year"] = datetime.year

        return transaction


class TransactionTimestampAssigner(TimestampAssigner):
    def __init__(self, settings: AppSettings):
        super().__init__()
        self.settings = settings

    def extract_timestamp(self, value, record_timestamp):
        dt = pendulum.parse(value["event_timestamp"], tz=self.settings.pipeline.tz)
        return int(dt.timestamp() * 1000)
