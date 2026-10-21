from typing_extensions import Optional
from pydantic import BaseModel

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment, TableDescriptor, Schema
from pyflink.datastream.formats.json import JsonRowDeserializationSchema, JsonRowSerializationSchema
from pyflink.common import Types
from pyflink.datastream.connectors.kafka import DeliveryGuarantee, KafkaRecordSerializationSchema, KafkaSink, KafkaSource, KafkaOffsetsInitializer

from models.endpoint import HiveEndpoint, KafkaEndpoint
from models.transaction import Transaction
from models.transaction_daily import TransactionDaily
from src.config.settings import AppSettings

from src.utils.hive_utils import HiveUtils
from src.utils.flink_utils import FlinkUtils

class BootstrapInitializer:

    def __init__(self, settings: AppSettings, env: StreamExecutionEnvironment):
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)

    def build_kafka_source(self, source: KafkaEndpoint, model: BaseModel) -> KafkaSource:
        username = source.username
        password = source.password.get_secret_value()

        bootstrap_servers = source.bootstrap_servers
        topic = source.topic

        schema = FlinkUtils.build_flink_schema(model, "streaming")

        deserializer = (
            JsonRowDeserializationSchema.builder()
            .type_info(
                Types.ROW_NAMED(
                    [name for name, _ in schema],
                    [type_ for _, type_ in schema]
                )
            )
            .build()
        )

        jaas = (
            "org.apache.kafka.common.security.plain.PlainLoginModule required "
            f'username="{username}" password="{password}";'
        )

        return (
            KafkaSource.builder()
            .set_bootstrap_servers(bootstrap_servers)
            .set_topics(topic)
            .set_starting_offsets(KafkaOffsetsInitializer.latest())
            .set_property("security.protocol", "SASL_PLAINTEXT")
            .set_property("sasl.mechanism", "PLAIN")
            .set_property("sasl.jaas.config", jaas)
            .set_value_only_deserializer(deserializer)
            .build()
        )

    def build_kafka_sink(self, sink: KafkaEndpoint, model: BaseModel):
        username = sink.username
        password = sink.password.get_secret_value()

        bootstrap_servers = sink.bootstrap_servers
        topic = sink.topic

        base_schema = FlinkUtils.build_flink_schema(model, "streaming")

        serializer = (
            JsonRowSerializationSchema.builder()
            .with_type_info(
                Types.ROW_NAMED(
                    [name for name, _ in base_schema],
                    [type_ for _, type_ in base_schema]
                )
            )
            .build()
        )

        jaas = (
            "org.apache.kafka.common.security.plain.PlainLoginModule required "
            f'username="{username}" password="{password}";'
        )

        return (
            KafkaSink.builder()
            .set_bootstrap_servers(bootstrap_servers)
            .set_record_serializer(
                KafkaRecordSerializationSchema.builder()
                .set_topic(topic)
                .set_value_serialization_schema(serializer)
                .build()
            )
            .set_delivery_guarantee(DeliveryGuarantee.EXACTLY_ONCE)
            .set_transactional_id_prefix("fraud-job-alerts")
            .set_property("security.protocol", "SASL_PLAINTEXT")
            .set_property("sasl.mechanism", "PLAIN")
            .set_property("sasl.jaas.config", jaas)
            .build()
        )

    def build_hive_sink(self, sink: HiveEndpoint, model: BaseModel):

        version = self.settings.hive.version
        table_name = sink.table

        base_hive = HiveUtils(
            self.t_env, 
            sink.catalog_name, 
            sink.default_database, 
            hive_version=version
        )

        base_schema = FlinkUtils.build_flink_schema(model, "table")
    
        table_schema = Schema.new_builder().from_fields(
            [name for name, _ in base_schema],
            [type_ for _, type_ in base_schema]
        )

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

        return None

    def initialize_bootstrap(self):
        pipeline = self.settings.pipeline

        source_model = Transaction
        sink_model = TransactionDaily

        for source in pipeline.sources:
            if isinstance(source, KafkaEndpoint):
                self.build_kafka_source(source, model=source_model)

        for sink in pipeline.sinks:
            if isinstance(sink, KafkaEndpoint):
                self.build_kafka_sink(sink, model=sink_model)
            elif isinstance(sink, HiveEndpoint):
                self.build_hive_sink(sink, model=sink_model)
    


if __name__ == "__main__":
    pass
