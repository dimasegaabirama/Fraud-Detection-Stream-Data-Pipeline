from logging import Logger

from pyflink.datastream import StreamExecutionEnvironment
from pyflink.table import StreamTableEnvironment

from src.common.names import SINK_HIVE_NAME, SINK_KAFKA_NAME, SOURCE_NAME
from src.config.settings import AppSettings
from src.models.endpoint import Endpoint, HiveEndpoint, KafkaEndpoint
from src.utils.hive_utils import HiveUtils


class BootstrapInitializer:
    def __init__(self, logger: Logger, settings: AppSettings, env: StreamExecutionEnvironment):
        self.logger = logger
        self.settings = settings
        self.env = env
        self.t_env = StreamTableEnvironment.create(env)

    @staticmethod
    def _extract_endpoint(sources_or_sinks: list[Endpoint], name: str) -> Endpoint:
        config = next((value for value in sources_or_sinks if value.name == name), None)
        if config is None:
            raise ValueError(f"Configuration not found: {name}")
        return config

    @staticmethod
    def _kafka_jaas_config(config: KafkaEndpoint) -> str:
        return (
            "org.apache.flink.kafka.shaded.org.apache.kafka.common.security.plain."
            f'PlainLoginModule required username="{config.username}" '
            f'password="{config.password}";'
        )

    def source_transactions(self, source_name: str) -> None:
        config = self._extract_endpoint(self.settings.pipeline.sources, source_name)
        if not isinstance(config, KafkaEndpoint):
            raise ValueError(f"Kafka source configuration expected: {source_name}")

        try:
            self.logger.info("Initialize Kafka source: %s", source_name)
            self.t_env.execute_sql(
                f"""
                    CREATE TABLE {source_name} (
                        event_id          STRING NOT NULL,
                        transaction_id    STRING NOT NULL,
                        user_id           STRING NOT NULL,
                        amount            DECIMAL(18, 2) NOT NULL,
                        currency          STRING NOT NULL,
                        segment           STRING NOT NULL,
                        transaction_type  STRING NOT NULL,
                        direction         STRING NOT NULL,
                        sender_account    STRING,
                        receiver_account  STRING,
                        merchant_id       STRING,
                        ip_address        STRING NOT NULL,
                        device_id         STRING NOT NULL,
                        device_type       STRING NOT NULL,
                        latitude          DOUBLE,
                        longitude         DOUBLE,
                        status            STRING NOT NULL,
                        event_timestamp   TIMESTAMP(3) NOT NULL
                    ) WITH (
                        'connector' = 'kafka',
                        'topic' = '{config.topic}',
                        'properties.bootstrap.servers' = '{config.bootstrap_servers}',

                        'properties.security.protocol' = 'SASL_PLAINTEXT',
                        'properties.sasl.mechanism' = 'PLAIN',
                        'properties.sasl.jaas.config' = '{self._kafka_jaas_config(config)}',

                        'scan.startup.mode' = 'latest-offset',
                        'format' = 'json',
                        'json.fail-on-missing-field' = 'false',
                        'json.ignore-parse-errors' = 'true'
                    )
                """
            )
        except Exception as error:
            raise ValueError(f"Failed to create Kafka source: {source_name}") from error

    def sink_kafka(self, sink_name: str) -> None:
        config = self._extract_endpoint(self.settings.pipeline.sinks, sink_name)
        if not isinstance(config, KafkaEndpoint):
            raise ValueError(f"Kafka sink configuration expected: {sink_name}")

        try:
            self.logger.info("Initialize Kafka sink: %s", sink_name)
            self.t_env.execute_sql(
                f"""
                    CREATE TABLE {sink_name} (
                        alert_id STRING,
                        transaction_id STRING,
                        user_id STRING,
                        fraud_type STRING,
                        final_score INT,
                        observed_value DECIMAL(20, 4),
                        threshold_value DECIMAL(20, 4),
                        event_time TIMESTAMP(3),
                        detected_at TIMESTAMP(3)
                    ) WITH (
                        'connector' = 'kafka',
                        'topic' = '{config.topic}',
                        'properties.bootstrap.servers' = '{config.bootstrap_servers}',

                        'properties.security.protocol' = 'SASL_PLAINTEXT',
                        'properties.sasl.mechanism' = 'PLAIN',
                        'properties.sasl.jaas.config' = '{self._kafka_jaas_config(config)}',

                        'format' = 'json',
                        'json.fail-on-missing-field' = 'false',
                        'json.ignore-parse-errors' = 'true'
                    )
                """
            )
        except Exception as error:
            raise ValueError(f"Failed to create Kafka sink: {sink_name}") from error

    def sink_hive(self, sink_name: str) -> None:
        config = self._extract_endpoint(self.settings.pipeline.sinks, sink_name)
        if not isinstance(config, HiveEndpoint):
            raise ValueError(f"Hive sink configuration expected: {sink_name}")

        table_path = f"{config.catalog}.{config.database}.{config.table}"

        try:
            self.logger.info("Create Hive table: %s", table_path)
            with HiveUtils.use_hive_dialect(self.t_env) as hive_dialect:
                catalog = hive_dialect.create_or_replace_catalog(
                    t_env=self.t_env,
                    catalog_name=config.catalog,
                    hive_conf_dir=config.hive_conf_dir,
                    hadoop_conf_dir=config.hadoop_conf_dir,
                )
                hive_dialect.create_or_replace_database(
                    t_env=self.t_env,
                    database_name=config.database,
                    catalog=catalog,
                )

                self.t_env.execute_sql(
                    f"""
                        CREATE TABLE IF NOT EXISTS {table_path} (
                            alert_id            STRING,
                            transaction_id      STRING,

                            user_id             STRING,
                            fraud_type          STRING,
                            tier                STRING,

                            observed_value      DOUBLE,
                            threshold_value     DOUBLE,
                            base_score          DOUBLE,
                            factor              DOUBLE,
                            final_score         DOUBLE,
                            evidence            MAP<STRING, STRING>,
                            group_key           STRING,

                            event_day           STRING,
                            event_month         STRING,
                            event_year          STRING,
                            event_time          TIMESTAMP,
                            detected_at         TIMESTAMP
                        )
                        PARTITIONED BY (day STRING, month STRING, year STRING)
                        STORED AS PARQUET
                        TBLPROPERTIES (
                            'parquet.compression' = 'SNAPPY',
                            'partition.time-extractor.timestamp-pattern' =
                                '$year-$month-$day 00:00:00',
                            'sink.partition-commit.trigger' = 'partition-time',
                            'sink.partition-commit.delay' = '1 d',
                            'sink.partition-commit.policy.kind' = 'metastore,success-file',
                            'auto-compaction' = 'true',
                            'compaction.small-files.avg-size' = '15MB',
                            'compaction.file-size' = '128MB'
                        );
                    """
                )
        except Exception as error:
            raise ValueError(f"Failed to create Hive sink table: {table_path}") from error

    def initialize(self) -> None:
        self.source_transactions(SOURCE_NAME)
        self.sink_hive(SINK_HIVE_NAME)
        self.sink_kafka(SINK_KAFKA_NAME)


if __name__ == "__main__":
    pass
