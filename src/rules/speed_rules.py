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


def haversine_km(lon1, lat1, lon2, lat2):
    r = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class SpeedRules(KeyedProcessFunction):

    fraud_type = FraudType.SPEED

    def __init__(self, settings: AppSettings):
        self.pipeline = settings.pipeline
        self.rules = BaseRules(settings=settings, fraud_type=self.fraud_type)

    def open(self, runtime_context: RuntimeContext):
        self.last_point = runtime_context.get_map_state(
            MapStateDescriptor("lookup_speed", Types.STRING(), Types.DOUBLE())
        )
        self.last_trx = runtime_context.get_state(
            ValueStateDescriptor("last_trx_id", Types.STRING())
        )

    def process_element(self, value, ctx: "KeyedProcessFunction.Context"):
        if value.get("transaction_id") == self.last_trx.value():
            return

        cleaned_txn = CleanedTransaction(**value)
        
        seg = cleaned_txn.segment
        lon = cleaned_txn.longitude
        lat = cleaned_txn.latitude

        ts = pendulum.parse(value["event_timestamp"]).timestamp()

        result = None
        speed_kmh = 0.0
        distance_km = 0.0
        elapsed_s = 0.0
        stale = False

        if not self.last_point.is_empty():
            prev_lon = self.last_point.get("longitude")
            prev_lat = self.last_point.get("latitude")
            prev_ts = self.last_point.get("timestamp")

            elapsed_s = ts - prev_ts
            if elapsed_s > 0:
                distance_km = haversine_km(prev_lon, prev_lat, lon, lat)
                speed_kmh = distance_km / (elapsed_s / 3600.0)
                result = self.rules.get_result(value=speed_kmh, segment=seg)
            else:
                stale = True

        if not stale:
            self.last_point.put("longitude", lon)
            self.last_point.put("latitude", lat)
            self.last_point.put("timestamp", float(ts))
            self.last_trx.update(value["transaction_id"])

        if result is None or result.level == ThresholdLevelType.NONE:
            return

        yield (
            FRAUD_ALERTS_TAG,
            cleaned_txn
        )

        yield cleaned_txn.to_fact_fraud_evaluations(score_result=result)
