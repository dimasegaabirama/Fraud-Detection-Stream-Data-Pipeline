from typing import Any
from pydantic import BaseModel, SecretStr, Field, field_validator, model_validator

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


class ApiSettings(BaseModel):
    version: str
    ttl_ms: int
    base_currency: str = Field(min_length=3, max_length=3)
    path: str
    urls: list[str]

    @model_validator(mode="after")
    def formatted_urls(self):
        path = self.path.format(version=self.version, currency=self.base_currency)
        self.urls = [f"{url}{path}" for url in self.urls]
        return self


class RulesSettings(BaseModel):
    pass
    # amount: FraudRule
    # device: FraudRule
    # ip_address: FraudRule
    # speed: FraudRule
    # velocity: FraudRule


class PipelineSettings(BaseModel):
    catalog: str
    database: str
    parallelism: int = Field(gt=0)
    state_backend: str
    checkpoint_interval: int = Field(gt=0)
    checkpoint_dir: str
    savepoint_dir: str | None = None
