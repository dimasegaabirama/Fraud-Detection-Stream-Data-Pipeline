from collections.abc import Mapping

from pydantic import BaseModel
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSink,
    KafkaSource,
)
from pyflink.table import StreamTableEnvironment, TableDescriptor

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

    def build_kafka_source(
        self, source: KafkaEndpoint, model: type[BaseModel]
    ) -> KafkaSource:
        return KafkaUtils.build_source(source, model)

    def build_kafka_sink(
        self, sink: KafkaEndpoint, model: type[BaseModel]
    ) -> KafkaSink:
        return KafkaUtils.build_sink(sink, model)

    def build_hive_sink(
        self, sink: HiveEndpoint, model: type[BaseModel]
    ) -> None:
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
                .schema(
                    table_schema.build()
                )
                .format("parquet")
                .partitioned_by("year", "month", "day")
                .option("sink.rolling-policy.file-size", "32MB")
                .option("sink.rolling-policy.rollover-interval", "20 min")
                .option("sink.rolling-policy.check-interval", "1 min")
                .option("auto-compaction", "true")
                .option("compaction.file-size", "128MB"),
                ignoreIfExists=True
            )

    def initialize_source(
        self,
        source_models: Mapping[str, type[BaseModel]]
    ) -> dict[str, KafkaSource]:
        pipeline = self.settings.pipeline
        
        sources = {}

        for source in pipeline.sources:
            try:
                if isinstance(source, KafkaEndpoint):
                    model = source_models[source.name]
                    sources[source.name] = self.build_kafka_source(source, model=model)
                else:
                    raise ValueError(f"Unsupported source type: {type(source)}")
            except KeyError as exc:
                raise ValueError(
                    f"No model configured for Kafka/Hive source '{source.name}'"
                ) from exc

        return sources

    def initialize_sink(
        self,
        sink_models: Mapping[str, type[BaseModel]]
    ) -> dict[str, KafkaSink | None]:
        pipeline = self.settings.pipeline
        
        sinks = {}

        for sink in pipeline.sinks:
            try:
                if isinstance(sink, KafkaEndpoint):
                    model = sink_models[sink.name]
                    sinks[sink.name] = self.build_kafka_sink(sink, model=model)

                elif isinstance(sink, HiveEndpoint):
                    model = sink_models[sink.name]
                    sinks[sink.name] = self.build_hive_sink(sink, model=model)
                else:
                    raise ValueError(f"Unsupported sink type: {type(sink)}")
            except KeyError as exc:
                raise ValueError(
                    f"No model configured for Kafka/Hive sink '{sink.name}'"
                ) from exc

        return sinks

if __name__ == "__main__":
    pass
