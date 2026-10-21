from typing_extensions import Union, Dict, Tuple, Optional, Literal

from pyflink.table import DataTypes
from pyflink.common import Types

from pydantic import BaseModel, Field

from src.models.enums import EnvType

class FlinkUtils:

    JSON_TO_FLINK = {
        ("string", None): (DataTypes.STRING(), Types.STRING()),
        ("integer", None): (DataTypes.BIGINT(), Types.LONG()),
        ("number", None): (DataTypes.DOUBLE(), Types.DOUBLE()),
        ("boolean", None): (DataTypes.BOOLEAN(), Types.BOOLEAN()),
        ("string", "date-time"): (DataTypes.TIMESTAMP(3), Types.SQL_TIMESTAMP()),
        ("string", "date"): (DataTypes.DATE(), Types.SQL_DATE()),
        ("string", "decimal"): (DataTypes.DECIMAL(18, 2), Types.BIG_DEC())
    }

    @classmethod
    def _resolve_prop(cls, prop: dict, defs: dict) -> Tuple[str, Union[str, None], bool]:
        nullable = False

        if "$ref" in prop:
            ref = defs[prop["$ref"].split("/")[-1]]
            return ref.get("type", "string"), None, nullable

        if "anyOf" in prop:
            options = [o for o in prop["anyOf"] if o.get("type") != "null"]
            nullable = len(options) != len(prop["anyOf"])
            if len(options) != 1:
                raise ValueError(f"Complex types not supported: {prop}")
            t, f, _ = cls._resolve_prop(options[0], defs)
            return t, f, nullable

        return prop["type"], prop.get("format"), nullable


    @classmethod
    def build_flink_schema(cls, model: BaseModel, env_type: Optional[Literal["table", "streaming"]] = None) -> Dict[str, Tuple]:
        schema = model.model_json_schema(mode="serialization")
        defs = schema.get("$defs", {})
        required = set(schema.get("required", []))

        fields = []
        for name, prop in schema["properties"].items():
            t, f, nullable = cls._resolve_prop(prop, defs)
            try:
                data_type, type_info = cls.JSON_TO_FLINK[(t, f)]
            except KeyError:
                raise ValueError(f"Type not mapped: field={name}, type={t}, format={f}")
            nullable = nullable or name not in required
            fields.append((name, data_type if nullable else data_type.not_null(), type_info))

        if env_type is not None:
            env_type = EnvType(env_type.upper())
            fields = {
                EnvType.STREAMING: [(x[0], x[2]) for x in fields],
                EnvType.TABLE: [(x[0], x[1]) for x in fields],
            }
            return fields[env_type]
        return fields