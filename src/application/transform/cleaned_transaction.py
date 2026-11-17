from logging import Logger
from contextlib import contextmanager

import pendulum
from pydantic import ValidationError
from pyflink.common import Types
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor

from src.application.transform.helpers import NormalizeTransaction
from src.common.tags import DEAD_LETTER_TAG, DUPLICATE_TAG
from src.common.format import TIMESTAMP_FORMAT
from src.config.settings import AppSettings

from src.contracts.side_events import DeadLetterEvents, DuplicateEvents
from src.contracts.raw_events import Transaction
from src.contracts.cleaned_events import CleanedTransaction


DEDUP_TTL_MS = 300000

class TransactionNormalization(KeyedProcessFunction):
    def __init__(self, logger: Logger, settings: AppSettings):
        self.logger = logger
        self.pipeline = settings.pipeline

    def open(self, runtime_context: RuntimeContext):
        self.seen = runtime_context.get_state(ValueStateDescriptor("seen", Types.BOOLEAN()))

    @contextmanager
    def dead_letter_on_failure(self, value: dict, ctx: KeyedProcessFunction.Context):
        try:
            transaction_data = Transaction.model_validate(value)
            yield transaction_data
        except ValidationError as exc:
            self.logger.debug(f"Error: transaction_id={ctx.get_current_key()}")
            yield DEAD_LETTER_TAG, DeadLetterEvents(info=f"Error: {str(exc)}", value=value)
            return

    def process_element(self, value, ctx: KeyedProcessFunction.Context):

        with self.dead_letter_on_failure(value, ctx) as txn_data:

            if self.seen.value():
                self.logger.debug(f"Duplicate: transaction_id={ctx.get_current_key()}")
                
                duplicate_data = DuplicateEvents(value=value)
                yield DUPLICATE_TAG, DuplicateEvents(value=value)
                return

            self.seen.update(True)

            event_timestamp = pendulum.parse(txn_data.event_timestamp)
            event_ms = int(event_timestamp.timestamp() * 1000)

            ctx.timer_service().register_event_time_timer(event_ms + DEDUP_TTL_MS)

            cleaned = NormalizeTransaction.map(value)

            yield CleanedTransaction(
                **cleaned,
                event_timestamp=event_timestamp.strftime(TIMESTAMP_FORMAT),
            )

    def on_timer(self, timestamp: int, ctx):
        self.seen.clear()
