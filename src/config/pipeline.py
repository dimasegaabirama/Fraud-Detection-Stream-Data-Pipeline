from typing_extensions import List, Optional
from pydantic import BaseModel, Field

from src.models.endpoint import Endpoint, KafkaEndpoint, HiveEndpoint


class PipelineSettings(BaseModel):
    tz: str
    catalog: str
    default_database: str
    parallelism: int = Field(gt=0)
    state_backend: str
    checkpoint_interval: int = Field(gt=0)
    checkpoint_dir: str
    savepoint_dir: Optional[str] = None
    sources: List[Endpoint]
    sinks: List[Endpoint]
    

if __name__ == "__main__":
    settings = PipelineSettings(
        catalog="my_catalog",
        default_database="my_database",
        parallelism=4,
        state_backend="rocksdb",
        checkpoint_interval=60000,
        checkpoint_dir="/path/to/checkpoints",
        savepoint_dir="/path/to/savepoints",
        sources=[
            HiveEndpoint(
                name="source_hive",
                type="hive",
                catalog_name=None,
                default_database=None,
                table="source_table"
            ),
            KafkaEndpoint(
                name="source_kafka",
                type="kafka",
                bootstrap_servers=None,
                topic="source_topic"
            )
        ],
        sinks=[
            HiveEndpoint(
                name="sink_hive",
                type="hive",
                table="sink_table"
            ),
            KafkaEndpoint(
                name="sink_kafka",
                type="kafka",
                bootstrap_servers=None,
                topic="sink_topic"
            )
        ]
    )

    print(settings.model_fields_set)