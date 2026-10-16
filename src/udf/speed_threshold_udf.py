from pyflink.table.types import TimestampType

from src.domain.enums import Segment
from src.models.threshold import FraudThreshold
from src.udf.base_threshold_udf import BaseThresholdUDF


class SpeedThresholdUDF(BaseThresholdUDF):
    def calculate_speed(
        self,
        lat_1: float,
        lon_1: float,
        lat_2: float,
        lon_2: float,
        t1: TimestampType,
        t2: TimestampType,
    ) -> float:
        
        import math

        lat_1, lon_1, lat_2, lon_2 = map(math.radians, [lat_1, lon_1, lat_2, lon_2])

        R = 6371.0
        dlat = lat_2 - lat_1
        dlon = lon_2 - lon_1

        a = math.sin(dlat / 2) ** 2 + math.cos(lat_1) * math.cos(lat_2) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c

        diff_sec = t2 - t1
        hours = diff_sec / 3600

        if hours > 0:
            speed = distance / hours
            return speed
        return 0.0

    def eval(
        self,
        segment: str,
        lat_1: float,
        lon_1: float,
        lat_2: float,
        lon_2: float,
        t1: TimestampType,
        t2: TimestampType,
    ) -> FraudThreshold:
        speed = self.calculate_speed(lat_1, lon_1, lat_2, lon_2, t1, t2)
        return self.rules.get_score(Segment(segment), speed)


if __name__ == "__main__":
    pass
