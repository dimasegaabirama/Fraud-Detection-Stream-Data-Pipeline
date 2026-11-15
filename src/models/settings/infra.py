from typing import Any
from pydantic import BaseModel, Field, SecretStr


class KafkaSettings(BaseModel):
    version: str
    bootstrap_servers: str
    username: str
    password: SecretStr


class HiveSettings(BaseModel):
    version: str
    hostname: str
    conf_dir: str
    warehouse_dir: str
    metastore_port: str = Field(min_length=4)
    server_port: str = Field(min_length=4)

    @property
    def metastore_url(self) -> str:
        return f"thrift://{self.hostname}:{self.metastore_port}"

    @property
    def server_url(self) -> str:
        return f"beeline://{self.hostname}:{self.server_port}"


class HadoopSettings(BaseModel):
    version: str
    hostname: str
    port: str = Field(min_length=4)
    conf_dir: str

    @property
    def url(self):
        return f"hdfs://{self.hostname}:{self.port}"


class RedisSettings(BaseModel):
    host: str
    port: str = Field(min_length=4)
    db: str
    username: str | None = None
    password: SecretStr | None = None
    socket_timeout: float | None = None
    socket_connect_timeout: float | None = None
    socket_keepalive: bool | None = None
    decode_responses: bool = False
    max_connections: int | None = None
    health_check_interval: int = 0
    retry: Any | None = None


class HiveSettings(BaseModel):
    version: str
    hostname: str
    conf_dir: str
    warehouse_dir: str
    metastore_port: str = Field(min_length=4)
    server_port: str = Field(min_length=4)

    @property
    def metastore_url(self) -> str:
        return f"thrift://{self.hostname}:{self.metastore_port}"

    @property
    def server_url(self) -> str:
        return f"beeline://{self.hostname}:{self.server_port}"