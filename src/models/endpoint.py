from typing import Annotated, Literal
from pydantic import BaseModel, SecretStr, Field, model_validator


class KafkaEndpoint(BaseModel):
    type: Literal["kafka"]
    bootstrap_servers: str | None = None
    username: str | None = None
    password: SecretStr | None = None
    topic: str
    group_id: str | None = None


class HiveEndpoint(BaseModel):
    type: Literal["hive"]
    catalog: str | None = None
    database: str | None = None
    table: str
    partitioned_by: list[str] | None = None
    hive_conf_dir: str | None = None
    hadoop_conf_dir: str | None = None

    @model_validator(mode="before")
    @classmethod
    def _validate_catalog_and_database(cls, value):
        if value.get("catalog") is None or value.get("database") is None:
            raise ValueError("Hive requires catalog or database")
        return value


Endpoint = Annotated[KafkaEndpoint | HiveEndpoint, Field(discriminator="type")]
