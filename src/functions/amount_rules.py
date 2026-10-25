from pyflink.datastream.functions import ProcessWindowFunction
from pyflink.datastream.state import MapStateDescriptor, Types


class AmountRulesFunction(ProcessWindowFunction):
    def open(self, runtime_context):
        self.rules_state_descriptor = MapStateDescriptor(
            "rules_state", Types.STRING, Types.PICKLED_BYTE_ARRAY
        )

    def process(self, key, context, elements, out):
        rules_state = context.global_state().get_map_state(self.rules_state_descriptor)

        for rule_key in rules_state.keys():
            rule = rules_state.get(rule_key)
            if rule is not None:
                for element in elements:
                    if rule.condition(element):
                        out.collect(rule.apply(element))


