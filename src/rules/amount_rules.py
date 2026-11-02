from src.models.enums import FraudType
from src.rules.base_rules import BaseRules

from pyflink.datastream.state import ListStateDescriptor, ListState
from pyflink.datastream.functions import FlatMapFunction, RuntimeContext

class _AmountRulesTransform(KeyedProcessFunction):
    def open(self, runtime_context: RuntimeContext):
        self.average_state = ListStateDescriptor(
            name="user_id_average_state",
            
        )



class AmountRules(BaseRules):

    FRAUD_TYPE = FraudType.AMOUNT

    def __init__(self, settings, **key_values: str):
        super().__init__(settings, **key_values)
        self.timeout = self.rule.timeout_ms
        self.key_by = self.rule.group_key

    def evaluate(self, value: float, **key_values: str) -> int:
        score = self.get_score(value, **key_values)
        return score

    