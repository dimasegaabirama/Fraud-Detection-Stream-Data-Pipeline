from typing import Literal, Optional, Dict
from pydantic import BaseModel, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from src.config.fraud_rules import (
    HADOOP_CONF_DIR,
    HIVE_CONF_DIR,
    PIPELINE_CATALOG,
    PIPELINE_DEFAULT_DATABASE,
    PIPELINE_CHECKPOINT_DIR,
    PIPELINE_SAVEPOINT_DIR
)

from src.domain.enums import JobMode


class KafkaSettings(BaseModel):
    username: str
    password: SecretStr
    bootstrap_servers: str


class HadoopSettings(BaseModel):
    hostname: str
    port: str
    conf_dir: str = HADOOP_CONF_DIR

    @property
    def url(self) -> str:
        return f"hdfs://{self.hostname}:{self.port}"
    

class HiveSettings(BaseModel):
    version: str
    hostname: str
    metastore_port: str
    server_port: str
    conf_dir: str = HIVE_CONF_DIR

    @property
    def metastore_url(self) -> str:
        return f"thrift://{self.hostname}:{self.metastore_port}"

    @property
    def server_url(self) -> str:
        return f"beeline://{self.hostname}:{self.server_port}"


class PipelineSettings(BaseModel):
    parallelism: int
    state_backend: str
    checkpoint_interval: int
    checkpoint_dir: str = PIPELINE_CHECKPOINT_DIR
    savepoint_dir: str = PIPELINE_SAVEPOINT_DIR
    catalog: str = PIPELINE_CATALOG
    default_database: str = PIPELINE_DEFAULT_DATABASE
    

class AppSettings(BaseSettings):
    kafka: KafkaSettings
    hadoop: HadoopSettings
    hive: HiveSettings
    pipeline: PipelineSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        env_nested_delimiter="__",
        extra="ignore",
    )

if __name__ == "__main__":
    settings = AppSettings()
    print(settings)