from pyflink.datastream import DataStream, StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment
from pyflink.datastream.formats.json import JsonRowDeserializationSchema
from pyflink.common import Types
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.common import WatermarkStrategy

from src.models.enums import FlowDirection
from src.models.transaction import Transaction

class BootstrapInitializer:

    def __init__(self, settings: str, env: StreamExecutionEnvironment):
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)

    def create_hive_catalog(self, flow_direction: FlowDirection):
        base_pipeline = getattr(self.settings.pipeline, flow_direction.value.lower())
        for pipeline_config in base_pipeline:
            self.t_env.catalog

    def build_kafka_source(self, source_config):
        username = self.settings.kafka.username
        password = self.settings.kafka.password.get_secret_value()

        bootstrap_servers = source_config.bootstrap_servers
        topic = source_config.topic

        deserializer = (
            JsonRowDeserializationSchema.builder()
            .type_info(
                Types.ROW_NAMED(
                    [name for name, _ in self.FIELDS],
                    [type_ for _, type_ in self.FIELDS],
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

    def initialize_source(self) -> DataStream:
        for source in self.settings.pipeline.sources:
            if source.type == "kafka":
                username = self.settings.kafka.username
                password = self.settings.kafka.password.get_secret_value()

                bootstrap_servers = source.bootstrap_servers
                topic = source.topic
                group_id = source.group_id
            
            elif source.type == "hive":
                catalog_name = source.catalog_name
                default_database = source.default_database
                table = source.table    

 
        deserializer = (
            JsonRowDeserializationSchema.builder()
            .type_info(
                Types.ROW_NAMED(
                    [name for name, _ in self.FIELDS],
                    [type_ for _, type_ in self.FIELDS],
                )
            )
            .build()
        )
 
        jaas = (
            "org.apache.kafka.common.security.plain.PlainLoginModule required "
            f'username="{username}" password="{password}";'
        )
 
        source = (
            KafkaSource.builder()
            .set_bootstrap_servers(self.settings.kafka.bootstrap_servers)
            .set_topics(self.settings.kafka.topic)
            .set_starting_offsets(KafkaOffsetsInitializer.latest())
            .set_property("security.protocol", "SASL_PLAINTEXT")
            .set_property("sasl.mechanism", "PLAIN")
            .set_property("sasl.jaas.config", jaas)
            .set_value_only_deserializer(deserializer)
            .build()
        )
 
        return self.env.from_source(
            source=source,
            watermark_strategy=WatermarkStrategy.no_watermarks(),
            source_name="transactions",
        )

    def initialize_sink(self) -> None:
        with self.create_hive_catalog():
            self.t_env.execute_sql("""
                CREATE TABLE IF NOT EXISTS txn_raw (
                    event_id STRING,
                    transaction_id STRING,
                    user_id STRING,
                    amount DOUBLE,
                    currency STRING,
                    status STRING,
                    transaction_type STRING,
                    direction STRING,
                    sender_account STRING,
                    receiver_account STRING,
                    merchant_id STRING,
                    ip_address STRING,
                    device_id STRING,
                    device_type STRING,
                    latitude DOUBLE,
                    longitude DOUBLE,
                    `year` STRING,
                    `month` STRING,
                    `day` STRING,
                    `timestamp` TIMESTAMP(3)
                ) STORED AS PARQUET
                PARTITIONED BY (`year` STRING, `month` STRING, `day` STRING)
                CLUSTERED BY (user_id) INTO 10 BUCKETS
                TBLPROPERTIES (
                    'parquet.compression' = 'SNAPPY'
                    'sink.partition-commit.trigger' = 'partition-time',
                    'partition.time-extractor.timestamp-pattern' = '$year-$month-$day 00:00:00',
                    'sink.partition-commit.delay' = '1 d',
                    'sink.partition-commit.watermark-time-zone' = 'Asia/Jakarta',
                    'sink.partition-commit.policy.kind' = 'metastore,success-file',
                    'auto-compaction' = 'true',
                    'compaction.file-size' = '128MB',
                    'sink.rolling-policy.file-size' = '128MB',
                    'sink.rolling-policy.rollover-interval' = '30 min',
                    'sink.rolling-policy.check-interval' = '1 min'
                );
            """)


if __name__ == "__main__":
    pass
