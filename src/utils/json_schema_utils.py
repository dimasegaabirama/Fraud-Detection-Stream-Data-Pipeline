from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel
from pyflink.common import Row


class JsonSchemaUtils:

    @classmethod
    def data_mapping(
        cls,
        value: Any,
        models: type[BaseModel],
    ) -> Mapping[str, Any]:
        if isinstance(value, Mapping):
            return value

        if isinstance(value, Row):
            column_names = models.model_fields.keys()
            if value.__dict__.get("_fields"):
                return value.as_dict()

            return dict(zip(column_names, value, strict=True))
        raise TypeError(f"Expected a transaction mapping or PyFlink Row, got {type(value)}")


    @classmethod
    def resolve_property(
        cls,
        prop: Mapping[str, Any],
        defs: Mapping[str, Any],
    ) -> tuple[str, str | None, bool]:
        nullable = False

        if "$ref" in prop:
            ref = defs[prop["$ref"].split("/")[-1]]
            return ref.get("type", "string"), ref.get("format"), nullable

        if "anyOf" in prop:
            options = [option for option in prop["anyOf"] if option.get("type") != "null"]
            nullable = len(options) != len(prop["anyOf"])
            if len(options) != 1:
                raise ValueError(f"Complex types not supported: {prop}")
            resolved_type, resolved_format, _ = cls.resolve_property(options[0], defs)
            return resolved_type, resolved_format, nullable

        return prop["type"], prop.get("format"), nullable
