#   ip_address:                   # distinct ip_address per user_id
#     window_ms: 600000           # 10 minutes
#     threshold:
#       low:    {value: 2, score: 10}
#       medium: {value: 4, score: 50}
#       high:   {value: 6, score: 80}
#     factors:
#       segment: {business: 1.5}  # offices share an IP (NAT)
#       transaction_type: {cashout: 0.8, withdrawal: 0.8, transfer: 0.9, refund: 1.1, top_up: 1.1}

import math

import pendulum
from pyflink.common import Types
from pyflink.datastream import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import MapStateDescriptor, ValueStateDescriptor

from src.config.settings import AppSettings
from src.models.enums import FraudType

from src.contracts.cleaned_events import CleanedTransaction
from src.rules.base_rules import BaseRules

from src.models.enums import ThresholdLevelType
from src.common.tags import FRAUD_ALERTS_TAG

class IpRules(KeyedProcessFunction):

    fraud_type = FraudType.IP_ADDRESS

    def __init__(self, settings: AppSettings):
        self.pipeline = settings.pipeline
        self.rules = BaseRules(settings=settings, fraud_type=self.fraud_type)

    def open(self, runtime_context: RuntimeContext):
        self.prev_ip = runtime_context.get_state(
            ValueStateDescriptor("prev_ip", Types.STRING())
        )
        self.ip_count = runtime_context.get_map_state(
            MapStateDescriptor("ip_count", Types.STRING(), Types.DOUBLE())
        )

    def process_element(self, value, ctx: "KeyedProcessFunction.Context"):

        cleaned_txn = CleanedTransaction(**value)
        
        ip_address = cleaned_txn.ip_address
        prev_ip = self.prev_ip.value
        
        if ip_address == prev_ip:
            return
        
        last_count = self.ip_count.get(ip_address) or 0
        last_count += 1

        self.ip_count.put(ip_address, last_count)
        self.prev_ip.update(ip_address)

        result = self.rules.get_result(last_count, direction=cleaned_txn.direction, transaction_type=cleaned_txn.transaction_type)

        yield (
            FRAUD_ALERTS_TAG, 
            cleaned_txn
        )

        yield cleaned_txn.to_fact_fraud_evaluations(score_result=result)