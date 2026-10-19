from typing_extensions import Literal, Optional, Annotated, Union

from pydantic import BaseModel, Field


class KafkaEndpoint(BaseModel):
    name: str
    type: Literal["kafka"]
    bootstrap_servers: Optional[str] = None
    topic: str
    group_id: Optional[str] = None


class HiveEndpoint(BaseModel):
    name: str
    type: Literal["hive"]
    catalog_name: Optional[str] = None
    default_database: Optional[str] = None
    table: str
    hive_conf_dir: Optional[str] = None
    hadoop_conf_dir: Optional[str] = None

Endpoint = Annotated[Union[KafkaEndpoint, HiveEndpoint], Field(discriminator="type")]