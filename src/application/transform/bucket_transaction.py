from logging import Logger
from functools import partial
from contextlib import contextmanager

import pendulum

from pyflink.common import Types
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor, ListStateDescriptor, MapStateDescriptor

from src.config.settings import AppSettings
from src.contracts.cleaned_events import CleanedTransaction


BUCKET_MS = 60_000
MAX_LOOKBACK_MS = 3_600_000  

class BucketWindowState(KeyedProcessFunction):

    fraud_rule = None

    def __init__(self, logger: Logger, settings: AppSettings):
        super().__init__()
        self.logger = logger
        self.settings = settings

    def open(self, runtime_context: RuntimeContext):
        self.bucket_lookup = runtime_context.get_map_state(
            MapStateDescriptor(
                "bucket_lookup",
                Types.INT(),
                Types.PICKLED_BYTE_ARRAY()
            )
        )
        self.oldest_ts = runtime_context.get_state(
            ValueStateDescriptor("oldest_ts", Types.BIG_INT())
        )

        self.last_ts = runtime_context.get_state(
            ValueStateDescriptor("last_ts", Types.BIG_INT())
        )

    def process_element(self, value, ctx: "KeyedProcessFunction.Context"):

        cleaned_txn = CleanedTransaction.model_validate(value)
        event_timestamp = cleaned_txn.event_timestamp_ms
        
        bucket_id = event_timestamp // BUCKET_MS
        items = self.bucket_lookup.get(bucket_id) or []
        items.append(cleaned_txn)

        self.bucket_lookup.put(bucket_id, items)

        last_ts = max(event_timestamp, self.last_ts.value() or 0)
        self.last_ts.update(last_ts)

        oldest_ts = self.oldest_ts.value()
        if oldest_ts is None or bucket_id < oldest_ts:
            oldest_ts = bucket_id

        cutoff_bucket = (last_ts - MAX_LOOKBACK_MS) // BUCKET_MS
        while oldest_ts < cutoff_bucket:
            self.bucket_lookup.remove(oldest_ts)
            oldest_ts += 1
        
        self.oldest_ts.update(oldest_ts)