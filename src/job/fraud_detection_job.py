from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment



class FraudDetectionJob:
    def __init__(self, settings: str, env: StreamExecutionEnvironment) -> None:
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)