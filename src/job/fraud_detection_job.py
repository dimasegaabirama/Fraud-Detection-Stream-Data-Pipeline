from pyflink.common import Types
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

from models.transaction_daily import TransactionDaily
from models.transaction_fraud import TransactionFraudAlert
from src.models.transaction import Transaction
from src.bootstrap.init_schema import BootstrapInitializer
from src.config.settings import AppSettings
from src.utils.kafka_utils import KafkaUtils



class FraudDetectionJob:
    def __init__(self, settings: AppSettings, env: StreamExecutionEnvironment) -> None:
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)

    def prepare_source_and_sink(self):

        source_models = {
            "kafka_source": Transaction,
        }

        sink_models = {
            "kafka_sink": TransactionFraudAlert,
            "hive_sink": TransactionDaily,
        }

        BootstrapInitializer(self.settings, self.env).initialize_source(source_models=source_models)
        BootstrapInitializer(self.settings, self.env).initialize_sink(source_models=source_models)