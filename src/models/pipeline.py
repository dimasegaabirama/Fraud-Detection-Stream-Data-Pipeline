from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator

from src.models.kafka import KafkaSettings
from src.models.endpoint import Endpoint, KafkaEndpoint, HiveEndpoint


class PipelineSettings(BaseModel):
    catalog: str
    default_database: str
    parallelism: int = Field(gt=0)
    state_backend: str
    checkpoint_interval: int = Field(gt=0)
    checkpoint_dir: str
    savepoint_dir: Optional[str] = None
    sources: List[Endpoint]
    sinks: List[Endpoint]

    @model_validator(mode="after")
    def set_default_sources_and_sinks(self):
        for endpoint in (*self.sources, *self.sinks):
            if isinstance(endpoint, HiveEndpoint):
                if endpoint.catalog_name is None:
                    endpoint.catalog_name = self.catalog
                if endpoint.default_database is None:
                    endpoint.default_database = self.default_database
            elif isinstance(endpoint, KafkaEndpoint):
                if endpoint.bootstrap_servers is None:
                    endpoint.bootstrap_servers = KafkaSettings().bootstrap_servers
        return self

if __name__ == "__main__":
    pass