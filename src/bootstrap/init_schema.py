from pydantic import BaseModel
from pyflink.common import Configuration
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSink,
    KafkaSource,
)
from pyflink.table import Schema, StreamTableEnvironment, TableDescriptor

from src.config.settings import AppSettings
from src.models.endpoint import HiveEndpoint, KafkaEndpoint
from src.models.transaction import Transaction
from src.models.transaction_daily import TransactionDaily
from src.models.transaction_fraud import TransactionFraudAlert
from src.utils.flink_utils import FlinkUtils
from src.utils.hive_utils import HiveUtils
from src.utils.kafka_utils import KafkaUtils


class BootstrapInitializer:

    def __init__(self, settings: AppSettings, env: StreamExecutionEnvironment):
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)

    def build_kafka_source(self, source: KafkaEndpoint, model: BaseModel) -> KafkaSource:
        return KafkaUtils.build_source(source, model)

    def build_kafka_sink(self, sink: KafkaEndpoint, model: BaseModel) -> KafkaSink:
        return KafkaUtils.build_sink(sink, model)

    def build_hive_sink(self, sink: HiveEndpoint, model: BaseModel) -> None:
        if sink.catalog_name is None or sink.default_database is None:
            raise ValueError(
                "Hive sink requires catalog_name and default_database"
            )

        version = self.settings.hive.version
        table_name = sink.table

        base_hive = HiveUtils(
            self.t_env,
            table_name=table_name,
            catalog_name=sink.catalog_name,
            database_name=sink.default_database,
            hive_conf_dir=sink.hive_conf_dir,
            hadoop_conf_dir=sink.hadoop_conf_dir,
            hive_version=version
        )

        table_schema = FlinkUtils.build_table_schema(model)

        base_hive.create_or_replace_catalog()
        base_hive.create_or_replace_database()

        with base_hive.use_hive_dialect() as hive_dialect:
            hive_dialect.create_table(
                table_name,
                TableDescriptor.for_connector("hive")
                .schema(
                    table_schema.build()
                )
                .format("parquet")
                .partitioned_by("year", "month", "day")
                .option("sink.rolling-policy.file-size", "32MB")
                .option("sink.rolling-policy.rollover-interval", "20 min")
                .option("sink.rolling-policy.check-interval", "1 min")
                .option("auto-compaction", "true")
                .option("compaction.file-size", "128MB")
            )

    def initialize_bootstrap(self) -> tuple[list[KafkaSource], list[KafkaSink]]:
        pipeline = self.settings.pipeline

        kafka_source_model = Transaction
        hive_sink_model = TransactionDaily
        kafka_sink_model = TransactionFraudAlert

        sources = []
        sinks = []

        for source in pipeline.sources:
            if isinstance(source, KafkaEndpoint):
                sources.append(
                    self.build_kafka_source(source, model=kafka_source_model)
                )

        for sink in pipeline.sinks:
            if isinstance(sink, KafkaEndpoint):
                sinks.append(
                    self.build_kafka_sink(sink, model=kafka_sink_model)
                )
            elif isinstance(sink, HiveEndpoint):
                self.build_hive_sink(sink, model=hive_sink_model)

        return sources, sinks

if __name__ == "__main__":
    config = Configuration()
    t_env = StreamExecutionEnvironment.get_execution_environment(config)

    pipeline_settings = AppSettings()
    kafka_source = pipeline_settings.pipeline.sources

    sources, sinks = BootstrapInitializer(pipeline_settings, t_env).initialize_bootstrap()
    
