from collections.abc import Mapping

from pydantic import BaseModel
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSink,
    KafkaSource,
)
from pyflink.table import StreamTableEnvironment, Table, TableDescriptor

from src.application.bootstrap.registry import SINK_REGISTRY, SOURCE_REGISTRY
from src.config.settings import AppSettings
from src.models.endpoint import HiveEndpoint, KafkaEndpoint
from src.utils.flink_utils import FlinkUtils
from src.utils.hive_utils import HiveUtils
from src.utils.kafka_utils import KafkaUtils


class BootstrapInitializer:

    def __init__(self, settings: AppSettings, env: StreamExecutionEnvironment):
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)

    @staticmethod
    def validate_model_mapping(
        models: Mapping[str, type[BaseModel]],
        endpoint_name: str,
        endpoint_type: str,
    ) -> type[BaseModel]:
        if endpoint_name not in models:
            raise ValueError(
                f"No model configured for {endpoint_type} '{endpoint_name}'"
            )
        return models[endpoint_name]

    def build_kafka_source(
        self,
        source: KafkaEndpoint,
        model: type[BaseModel],
    ) -> KafkaSource:
        return KafkaUtils.build_source(source, model)

    def build_kafka_sink(
        self,
        sink: KafkaEndpoint,
        model: type[BaseModel],
    ) -> KafkaSink:
        return KafkaUtils.build_sink(sink, model)

    def build_hive_sink(
        self,
        sink: HiveEndpoint,
        model: type[BaseModel],
    ) -> Table:
        if sink.catalog_name is None or sink.default_database is None:
            raise ValueError(
                "Hive sink requires catalog_name and default_database"
            )

        version = self.settings.hive.version
        table_name = sink.table

        catalog = HiveUtils.create_or_replace_catalog(
            self.t_env,
            sink.catalog_name,
            hive_conf_dir=sink.hive_conf_dir,
            hadoop_conf_dir=sink.hadoop_conf_dir,
            hive_version=version,
        )

        HiveUtils.create_or_replace_database(
            self.t_env,
            sink.catalog_name,
            sink.default_database,
            catalog=catalog,
        )
        table_schema = FlinkUtils.build_table_schema(model)

        with HiveUtils.use_hive_dialect(self.t_env) as hive_dialect:
            hive_dialect.create_table(
                table_name,
                TableDescriptor.for_connector("hive")
                .schema(table_schema.build())
                .format("parquet")
                .partitioned_by("year", "month", "day")
                .option("sink.rolling-policy.file-size", "32MB")
                .option("sink.rolling-policy.rollover-interval", "20 min")
                .option("sink.rolling-policy.check-interval", "1 min")
                .option("auto-compaction", "true")
                .option("compaction.file-size", "128MB"),
                ignoreIfExists=True,
            )

        return self.t_env.from_path(f"{sink.catalog_name}.{sink.default_database}.{table_name}")

    def initialize_sources(
        self
    ) -> dict[str, KafkaSource]:
        pipeline = self.settings.pipeline
        sources: dict[str, KafkaSource] = {}

        for source in pipeline.sources:
            if not isinstance(source, KafkaEndpoint):
                raise ValueError(f"Unsupported source type: {type(source)}")

            model = self.validate_model_mapping(
                models=SOURCE_REGISTRY,
                endpoint_name=source.name,
                endpoint_type="Kafka source"
            )
            sources[source.name] = self.build_kafka_source(source, model)

        return sources

    def initialize_sinks(
        self
    ) -> dict[str, KafkaSink | None]:
        pipeline = self.settings.pipeline
        sinks: dict[str, KafkaSink | None] = {}

        for sink in pipeline.sinks:
            if isinstance(sink, KafkaEndpoint):
                model = self.validate_model_mapping(
                    models=SINK_REGISTRY,
                    endpoint_name=sink.name,
                    endpoint_type="Kafka sink"
                )
                sinks[sink.name] = self.build_kafka_sink(sink, model)
                continue

            if isinstance(sink, HiveEndpoint):
                model = self.validate_model_mapping(
                    models=SINK_REGISTRY,
                    endpoint_name=sink.name,
                    endpoint_type="Hive sink",
                )
                sinks[sink.name] = self.build_hive_sink(sink, model)
                continue

            raise ValueError(f"Unsupported sink type: {type(sink)}")

        return sinks

if __name__ == "__main__":
    pass
