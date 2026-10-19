from typing_extensions import Dict, Literal

from pyflink.table import DataTypes
from pyflink.common import Types

from pydantic import BaseModel, Field

class FlinkUtils:

    PY_TO_FLINK_TYPES = {
        "str": (DataTypes.STRING(), Types.STRING()),
        "int": (DataTypes.BIGINT(), Types.LONG()),
        "float": (DataTypes.DOUBLE(), Types.DOUBLE()),
        "bool": (DataTypes.BOOLEAN(), Types.BOOLEAN()),
        "decimal": (DataTypes.DECIMAL(18, 2), Types.BIG_DEC()),
        "datetime": (DataTypes.TIMESTAMP(3), Types.SQL_TIMESTAMP()),
        "date": (DataTypes.DATE(), Types.SQL_DATE()),
    }

    @classmethod
    def model_to_flink_schema(cls, model: BaseModel, env_type: Literal["table", "stream"]) -> Dict[str, tuple]:
        """Convert a Pydantic model to a Flink schema."""
        model_json = model.model_dump()

        flink_schema = {}
        for field_name, field_value in model_json.items():
            field_type = type(field_value).__name__
            if field_type in cls.PY_TO_FLINK_TYPES:
                flink_schema[field_name] = cls.PY_TO_FLINK_TYPES[field_type][0 if env_type == "table" else 1]
            else:
                raise ValueError(f"Unsupported field type: {field_type} for field: {field_name}")
        return flink_schema