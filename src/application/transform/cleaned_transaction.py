from logging import Logger

import pendulum
from pydantic import ValidationError
from pyflink.common import Types
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor

from src.application.transform.helpers import NormalizeTransaction
from src.common.tags import DEAD_LETTER_TAG, DUPLICATE_TAG
from src.common.ttl import DEDUP_TTL_MS
from src.common.format import TIMESTAMP_FORMAT
from src.config.settings import AppSettings
from src.contracts.raw_events import Transaction
from src.contracts.cleaned_events import CleanedTransaction


class TransactionNormalization(KeyedProcessFunction):
    def __init__(self, logger: Logger, settings: AppSettings):
        self.logger = logger
        self.pipeline = settings.pipeline

    def open(self, runtime_context: RuntimeContext):
        self.seen = runtime_context.get_state(ValueStateDescriptor("seen", Types.BOOLEAN()))

    def process_element(self, value, ctx: KeyedProcessFunction.Context):
        try:
            transaction_data = Transaction.model_validate(value)
        except ValidationError as exc:
            yield DEAD_LETTER_TAG, {"raw": value, "error": str(exc)}
            return

        if self.seen.value():
            self.logger.debug(f"Duplicate transaction_id={ctx.get_current_key()}")
            yield DUPLICATE_TAG, value
            return

        self.seen.update(True)

        event_timestamp = pendulum.parse(transaction_data.event_timestamp)

        event_ms = int(event_timestamp.timestamp() * 1000)
        ctx.timer_service().register_event_time_timer(event_ms + DEDUP_TTL_MS)

        try:
            cleaned = NormalizeTransaction.map(value)
        except Exception as exc:
            yield DEAD_LETTER_TAG, {"raw": value, "error": f"normalize: {exc}"}
            return

        yield CleanedTransaction(
            **cleaned,
            event_timestamp=event_timestamp.strftime(TIMESTAMP_FORMAT),
        )

    def on_timer(self, timestamp: int, ctx):
        self.seen.clear()
