from pathlib import Path

from pydantic import model_validator, BaseModel
from src.models.endpoint import Endpoint


SourceSettings = dict[str, Endpoint]
SinkSettings = dict[str, Endpoint]