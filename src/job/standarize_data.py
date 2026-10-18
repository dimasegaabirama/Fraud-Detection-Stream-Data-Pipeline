from pyflink.datastream import StreamExecutionEnvironment
from pyflink.common import Types
from pyflink.table import StreamTableEnvironment
from pyflink.datastream.functions import MapFunction


from src.config.settings import AppSettings
from src.rules import AmountRules, VelocityRules
from src.udf.base_threshold_udf import BaseThresholdUDF