from contextlib import contextmanager
from typing_extensions import Iterator

from pyflink.table import SqlDialect
from pyflink.table.catalog import HiveCatalog
from pyflink.table import EnvironmentSettings, StreamTableEnvironment
from src.config.settings import AppSettings

class FlinkInitializer:
    def __init__(self, settings: AppSettings, t_env: StreamTableEnvironment):
        self.settings = settings
        self.t_env = t_env

    def initialize(self) -> None:
        self.initialize_source_tables()
        self.initialize_hive_tables()
        return None

    def initialize_source_tables(self) -> None:

        topic = self.settings.kafka.topic
        kafka_username = self.settings.kafka.username
        kafka_password = self.settings.kafka.password.get_secret_value()
        bootstrap_servers = self.settings.kafka.bootstrap_servers

        source_tables = f"""
            CREATE TABLE transactions (
                event_id STRING,
                transaction_id STRING,
                user_id STRING,
                `timestamp` TIMESTAMP(3),
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
                WATERMARK FOR `timestamp` AS `timestamp` - INTERVAL '5' SECOND
            ) WITH (
                'connector' = 'kafka',
                'topic' = '{topic}',
                'properties.bootstrap.servers' = '{bootstrap_servers}',
                'properties.group.id' = 'fraud-detection',
                'scan.startup.mode' = 'earliest-offset',
                'format' = 'json',
                'json.timestamp-format.standard' = 'SQL'

                'properties.security.protocol' = 'SASL_PLAINTEXT',
                'properties.sasl.mechanism' = 'PLAIN',
                'properties.sasl.jaas.config' = 'org.apache.kafka.common.security.plain.PlainLoginModule required username="{kafka_username}" password="{kafka_password}";'
            );
        """

        self.t_env.execute_sql(source_tables.format(
            topic=topic,
            bootstrap_servers=bootstrap_servers,
            kafka_username=kafka_username,
            kafka_password=kafka_password
        ))

    @contextmanager
    def create_hive_catalog(self):
        hive_catalog = HiveCatalog(
            catalog_name=self.settings.pipeline.catalog,
            default_database=self.settings.pipeline.default_database,
            hive_conf_dir=self.settings.hive.conf_dir,
            hadoop_conf_dir=self.settings.hadoop.conf_dir,
            hive_version=self.settings.hive.version
        )
        self.t_env.register_catalog(self.settings.pipeline.catalog, hive_catalog)
        self.t_env.use_catalog(self.settings.pipeline.catalog)
        self.t_env.get_config().set_sql_dialect(SqlDialect.HIVE)
        try:
            yield hive_catalog
        finally:
            self.t_env.get_config().set_sql_dialect(SqlDialect.DEFAULT)


    def initialize_hive_tables(self) -> None:
        with self.create_hive_catalog():
            self.t_env.execute_sql(f"""
                CREATE TABLE IF NOT EXISTS txn_raw (
                    event_id STRING,
                    transaction_id STRING,
                    user_id STRING,
                    `timestamp` TIMESTAMP(3),
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
                    longitude DOUBLE
                ) STORED AS PARQUET
                PARTITIONED BY (`timestamp`)
                CLUSTERED BY (user_id) INTO 10 BUCKETS
                TBLPROPERTIES (
                    'parquet.compression' = 'SNAPPY'
                );
            """)

if __name__ == "__main__":
    settings = AppSettings()
    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = StreamTableEnvironment.create(environment_settings=env_settings)

    flink_initializer = FlinkInitializer(settings, t_env)
    flink_initializer.initialize()

