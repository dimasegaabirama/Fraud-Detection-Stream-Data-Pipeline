from src.models.enums import FraudType
from src.rules.base_rules import BaseRules
from src.config.settings import AppSettings

from pyflink.datastream.state import ListStateDescriptor, ListState, StateTtlConfig, Time,
from pyflink.datastream.functions import FlatMapFunction, RuntimeContext, KeyedProcessFunction

class _AmountRulesTransform(KeyedProcessFunction):

    def __init__(self, settings: AppSettings):
        self.settings = settings

    def open(self, runtime_context: RuntimeContext):
        self.avg_state = ListStateDescriptor(
            name="amount_avg_state"
        )
        self.ttl_config = StateTtlConfig.new_builder(ttl=Time.minutes(5))

        self.average_state.enable_time_to_live()
        self.state = runtime_context.get_list_state(self.average_state)

    # def process_element(self, value, ctx: KeyedProcessFunction.Context):


class AmountRules(BaseRules):

    FRAUD_TYPE = FraudType.AMOUNT

    def __init__(self, settings, **key_values: str):
        super().__init__(settings, **key_values)
        self.timeout = self.rule.timeout_ms
        self.key_by = self.rule.group_key

    def evaluate(self, value: float, **key_values: str) -> int:
        score = self.get_score(value, **key_values)
        return score

    