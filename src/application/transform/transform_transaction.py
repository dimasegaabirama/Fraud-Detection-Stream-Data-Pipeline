from logging import Logger
from contextlib import contextmanager
from typing import Any

import pendulum
from pydantic import ValidationError
from pyflink.common import Types, Time
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor, StateTtlConfig

from src.application.transform.helpers import NormalizeTransaction
from src.common.tags import DEAD_LETTER_TAG, DUPLICATE_TAG, BLACKLIST_TAG
from src.common.format import TIMESTAMP_FORMAT
from src.config.settings import AppSettings

from src.contracts.side_events import DeadLetterEvent, DuplicateEvent, BlacklistEvent
from src.contracts.raw_events import Transaction
from src.contracts.cleaned_events import CleanedTransaction

from src.integrations.redis.blacklist import BlacklistClient

DEDUP_TTL_MS = 300_000

class TransformTransaction(KeyedProcessFunction):
    def __init__(self, logger, settings, blacklist_client):
        self.logger = logger
        self.pipeline = settings.pipeline
        self.blacklist_client = blacklist_client

    def open(self, runtime_context: RuntimeContext):
        ttl_config = StateTtlConfig(
            update_type=StateTtlConfig.UpdateType.OnCreateAndWrite,
            state_visibility=StateTtlConfig.StateVisibility.NeverReturnExpired,
            ttl=Time.milliseconds(DEDUP_TTL_MS),
            cleanup_strategies=StateTtlConfig.CleanupStrategies.RocksdbCompactFilterCleanupStrategy(1000)
        )

        self.seen = runtime_context.get_state(
            ValueStateDescriptor("seen", Types.BOOLEAN()).enable_time_to_live(
                ttl_config=ttl_config
            )
        )


    def _blacklist_reason(self, txn: Transaction) -> str | None:
        if self.blacklist_client.is_user_id_blacklist(user_id=txn.user_id):
            return "USER_ID BLACKLIST"
        if self.blacklist_client.is_ip_address_blacklist(ip_address=txn.ip_address):
            return "IP_ADDRESS BLACKLIST"
        return None

    def _get_processed_timestamp(self, ctx) -> int:
        return ctx.timer_service().current_processing_time()

    def _get_event_timestamp(self, text: str) -> int:
        return int(pendulum.parse(text).timestamp() * 1000)

    def process_element(self, value, ctx: "KeyedProcessFunction.Context"):

        try:
            txn = Transaction.model_validate(value)

            reason = self._blacklist_reason(txn)
            if reason:
                self.logger.debug(f"Blacklist: transaction_id={ctx.get_current_key()}, reason={reason}")
                yield BLACKLIST_TAG, BlacklistEvent(info=reason, value=txn)
                return

            if self.seen.value():
                self.logger.debug(f"Duplicate: transaction_id={ctx.get_current_key()}")
                yield DUPLICATE_TAG, DuplicateEvent(value=txn)
                return
            
            self.seen.update(True)

            cleaned = NormalizeTransaction.map(value)
            cleaned_transaction = CleanedTransaction(
                **cleaned,
                event_timestamp_ms=self._get_event_timestamp(txn.event_timestamp),
                processed_timestamp_ms=self._get_processed_timestamp(ctx),
            )

            yield cleaned_transaction

        except ValidationError as exc:
            self.logger.debug(f"Invalid: transaction_id={ctx.get_current_key()}")
            yield DEAD_LETTER_TAG, DeadLetterEvent(info=f"ERROR: {exc}", value=value)
