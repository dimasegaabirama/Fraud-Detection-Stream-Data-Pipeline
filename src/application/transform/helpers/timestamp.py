import pendulum
from pyflink.common.watermark_strategy import TimestampAssigner

from src.config.settings import AppSettings


class TransactionTimestampAssigner(TimestampAssigner):
    def __init__(self, settings: AppSettings, column_name: str = "event_timestamp"):
        super().__init__()
        self.settings = settings
        self.column_name = column_name

    def extract_timestamp(self, value, record_timestamp):
        dt = pendulum.parse(value[self.column_name], tz=self.settings.pipeline.tz)
        return int(dt.timestamp() * 1000)
