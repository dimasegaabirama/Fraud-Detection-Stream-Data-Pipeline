from pyflink.datastream.functions import BroadcastProcessFunction
from pyflink.datastream.state import MapStateDescriptor, Types

broadcast_state_descriptor = MapStateDescriptor("rules_state", Types.STRING, Types.STRING)


class BroadcastFunction(BroadcastProcessFunction):
    def open(self, runtime_context):
        self.broadcast_state_descriptor = broadcast_state_descriptor

    def process_broadcast_element(self, value, ctx):
        broadcast_state = ctx.get_broadcast_state(self.broadcast_state_descriptor)

        for key in value.keys():
            broadcast_state.put(key, value[key])

    def process_element(self, value, ctx):
        broadcast_state = ctx.get_broadcast_state(self.broadcast_state_descriptor)
