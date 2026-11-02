import json
from typing import Any

from pyflink.common import Types
from pyflink.common.time import Time
from pyflink.datastream.functions import KeyedProcessFunction, ProcessWindowFunction, RuntimeContext
from pyflink.datastream.state import StateTtlConfig, ValueStateDescriptor


class LatestPerTransactionByWindow(ProcessWindowFunction):
    def __init__(self):
        super().__init__()

    def process(self, key: Any, context: Any, elements: Any):
        yield max(elements, key=lambda element: element["event_timestamp"])


class LatestPerTransactionByTime(KeyedProcessFunction):
    def __init__(self, timeout_ms: int, settings, done_ttl_hours: int = 1):
        super().__init__()
        self.timeout_ms = timeout_ms
        self.settings = settings
        self.done_ttl_hours = done_ttl_hours

    def open(self, runtime_context: RuntimeContext):
        self.latest = runtime_context.get_state(
            ValueStateDescriptor("latest", Types.STRING()))
        self.latest_ts = runtime_context.get_state(
            ValueStateDescriptor("latest_ts", Types.LONG()))
        self.timer_ts = runtime_context.get_state(
            ValueStateDescriptor("timer_ts", Types.LONG()))

        done_desc = ValueStateDescriptor("done_ts", Types.LONG())
        done_desc.enable_time_to_live(
            StateTtlConfig.new_builder(Time.hours(self.done_ttl_hours))
            .set_update_type(StateTtlConfig.UpdateType.OnCreateAndWrite)
            .set_state_visibility(StateTtlConfig.StateVisibility.NeverReturnExpired)
            .build()
        )
        self.done = runtime_context.get_state(done_desc)

    def process_element(self, value: Any, ctx: KeyedProcessFunction.Context):
        ts_ms = int(value["event_timestamp"].timestamp() * 1000)

        done = self.done.value()
        if done is not None and ts_ms <= done:
            return

        current = self.latest_ts.value()
        if current is not None and ts_ms <= current:
            return

        self.latest.update(json.dumps(value, default=str))
        self.latest_ts.update(ts_ms)

        if self.timer_ts.value() is None:
            deadline = ctx.timestamp() + self.timeout_ms
            ctx.timer_service().register_event_time_timer(deadline)
            self.timer_ts.update(deadline)

    def on_timer(self, timestamp: int, ctx: KeyedProcessFunction.OnTimerContext):
        raw = self.latest.value()
        if raw is not None:
            self.done.update(self.latest_ts.value())
            yield raw

        self.latest.clear()
        self.latest_ts.clear()
        self.timer_ts.clear()
