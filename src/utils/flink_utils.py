from typing import Any, Literal

from pydantic import BaseModel
from pyflink.common import Types
from pyflink.table import DataTypes, Schema

from src.utils.json_schema_utils import JsonSchemaUtils


class FlinkUtils:
    JSON_TO_FLINK = {
        ("string", None): (DataTypes.STRING(), Types.STRING()),
        ("integer", None): (DataTypes.BIGINT(), Types.LONG()),
        ("number", None): (DataTypes.DOUBLE(), Types.DOUBLE()),
        ("boolean", None): (DataTypes.BOOLEAN(), Types.BOOLEAN()),
        ("string", "date-time"): (DataTypes.TIMESTAMP(3), Types.SQL_TIMESTAMP()),
        ("string", "date"): (DataTypes.DATE(), Types.SQL_DATE()),
        ("string", "decimal"): (DataTypes.DECIMAL(18, 2), Types.BIG_DEC()),
    }

    @classmethod
    def build_flink_schema(
        cls,
        model: type[BaseModel],
        env_type: Literal["table", "streaming"] | None = None,
    ) -> list[tuple[str, Any]] | list[tuple[str, Any, Any]]:
        schema = model.model_json_schema(mode="serialization")
        defs = schema.get("$defs", {})
        required = set(schema.get("required", []))

        fields = []
        for name, prop in schema["properties"].items():
            t, f, nullable = JsonSchemaUtils.resolve_property(prop, defs)
            try:
                data_type, type_info = cls.JSON_TO_FLINK[(t, f)]
            except KeyError as exc:
                raise ValueError(
                    f"Type not mapped: field={name}, type={t}, format={f}"
                ) from exc
            nullable = nullable or name not in required
            fields.append((name, data_type if nullable else data_type.not_null(), type_info))

        if env_type == "streaming":
            return [(name, type_info) for name, _, type_info in fields]
        if env_type == "table":
            return [(name, data_type) for name, data_type, _ in fields]
        return fields

    @classmethod
    def build_row_type_info(cls, model: type[BaseModel]):
        schema = cls.build_flink_schema(model, "streaming")
        return Types.ROW_NAMED(
            [name for name, _ in schema],
            [type_info for _, type_info in schema],
        )

    @classmethod
    def build_table_schema(cls, model: type[BaseModel]):
        fields = cls.build_flink_schema(model, "table")
        return Schema.new_builder().from_fields(
            [name for name, _ in fields],
            [data_type for _, data_type in fields],
        )


if __name__ == "__main__":
    pass
