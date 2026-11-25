from logging import Logger
from contextlib import contextmanager

import pendulum
from pydantic import ValidationError
from pyflink.common import Types
from pyflink.datastream.functions import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import ValueStateDescriptor, MapStateDescriptor

from src.config.settings import AppSettings


class BucketWindowState:
    def __init__(self):
        pass

    def get_max_window(self):
        



# class BucketedTransaction(KeyedProcessFunction):
    # def __init__(self, logger: Logger, settings: AppSettings):
    #     self.logger = logger
    #     self.pipeline = settings.pipeline

    # def open(self, runtime_context: RuntimeContext):
    #     self.bucket_lookup = runtime_context.get_map_state(
    #         MapStateDescriptor("bucket_lookup", Types.STRING(), Types.ROW_NAMED(
    #             ["count", "sum", "last_value", "ts"],
    #             [Types.INT(), Types.DOUBLE(), Types.STRING(), Types.LONG()]
    #         ))
    #     )

    # def process_element(self, value, ctx: KeyedProcessFunction.Context):
        

    # def on_timer(self, timestamp: int, ctx: "KeyedProcessFunction.OnTimerContext"):
    #     self.seen.clear()
