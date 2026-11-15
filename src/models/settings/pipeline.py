from pydantic import BaseModel, Field

class PipelineSettings(BaseModel):
    catalog: str
    database: str
    parallelism: int = Field(gt=0)
    state_backend: str
    checkpoint_interval: int = Field(gt=0)
    checkpoint_dir: str
    savepoint_dir: str | None = None
