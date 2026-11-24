from pyflink.common import Types
from pyflink.datastream import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import MapStateDescriptor, ValueStateDescriptor

from src.config.settings import AppSettings
from src.models.enums import FraudType

from src.contracts.cleaned_events import CleanedTransaction
from src.rules.base_rules import BaseRules

from src.common.tags import FRAUD_ALERTS_TAG


class DeviceRules(KeyedProcessFunction):

    fraud_type = FraudType.DEVICE

    def __init__(self, settings: AppSettings):
        self.pipeline = settings.pipeline
        self.rules = BaseRules(settings=settings, fraud_type=self.fraud_type)

    def open(self, runtime_context: RuntimeContext):
        self.prev_device = runtime_context.get_state(
            ValueStateDescriptor("prev_device", Types.STRING())
        )
        self.bucket = runtime_context.get_map_state(
            MapStateDescriptor("bucket_device", Types.STRING(), Types.LONG())
        )

    def process_element(self, value, ctx: "KeyedProcessFunction.Context"):

        cleaned_txn = CleanedTransaction(**value)
        
        device = cleaned_txn.device_type
        prev_device = self.prev_device.value
        
        if device == prev_device:
            return
        
        last_count = self.device_count.get(device) or 0
        last_count += 1

        self.device_count.put(device, last_count)
        self.prev_device.update(device)

        result = self.rules.get_result(last_count, direction=cleaned_txn.direction, transaction_type=cleaned_txn.transaction_type)

        yield (
            FRAUD_ALERTS_TAG, 
            cleaned_txn
        )

        yield cleaned_txn.to_fact_fraud_evaluations(score_result=result)


