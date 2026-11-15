import math

import pendulum
from pyflink.common import Types
from pyflink.datastream import KeyedProcessFunction, RuntimeContext
from pyflink.datastream.state import MapStateDescriptor, ValueStateDescriptor

from src.config.settings import AppSettings
from src.models.enums import FraudType
# from src.models.sink.fact_fraud_evaluations import FactFraudEvaluations
# from src.models.sink.fraud_alerts import FraudAlerts

from src.contracts.cleaned_events import CleanedTransaction
from src.rules.base_rules import BaseRules

from src.models.threshold import ThresholdLevel
from src.models.score import ScoreResult
from src.common.format import TIMESTAMP_FORMAT


def haversine_km(lon1, lat1, lon2, lat2):
    r = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = phi2 - phi1
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


class SpeedRules(KeyedProcessFunction):

    type = FraudType.SPEED

    def __init__(self, settings: AppSettings):
        self.pipeline = settings.pipeline
        self.rules = BaseRules(settings=settings, fraud_type=self.type)

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

        if result is None or result.level == ThresholdLevel.NONE:
            return

        now_ms = ctx.timer_service().current_processing_time()
        detected_at = pendulum.from_timestamp(now_ms / 1000).strftime(TIMESTAMP_FORMAT)

        score_result = ScoreResult(

        )

        observed_value = round(speed_kmh, 4)
        threshold_value = round(result.threshold_value, 4)
        base_score = result.base_score
        factor = round(result.factor, 4)
        final_score = result.final_score

        yield (
            FRAUD_RESULTS,
            cleaned_txn.to_fraud_alerts()
        )

        yield FactFraudEvaluations(
            alert_id=alert_id,
            transaction_id=transaction_id,
            user_id=value["user_id"],
            fraud_type=FraudType.SPEED,
            level=result.level,
            observed_value=observed_value,
            threshold_value=threshold_value,
            base_score=base_score,
            factor=factor,
            final_score=final_score,
            evidence={
                "speed_kmh": round(speed_kmh, 4),
                "distance_km": round(distance_km, 4),
                "elapsed_seconds": round(elapsed_s, 2),
                "segment": str(seg),
            },
            group_key=group_key,
            day=event_dt.day,
            month=event_dt.month,
            year=event_dt.year,
            event_time=event_dt,
            detected_at=detected_at,
        )
