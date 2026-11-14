from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from decimal import Decimal
from typing import Any

import pendulum
from pyflink.common import Row


class NormalizeTransaction:
    """Normalize raw transaction maps/rows for downstream processing."""

    _lowercase_fields = {"segment", "transaction_type", "direction", "device_type", "status"}
    _uppercase_fields = {"currency"}
    _decimal_fields = {"amount"}
    _float_fields = {"latitude", "longitude"}

    @staticmethod
    def _to_mapping(value: Any) -> dict[str, Any]:
        if isinstance(value, Row):
            if hasattr(value, "as_dict"):
                return value.as_dict()
            if hasattr(value, "_asdict"):
                return value._asdict()

        if isinstance(value, Mapping):
            return dict(value)

        if hasattr(value, "__dict__"):
            return {key: getattr(value, key) for key in vars(value) if not key.startswith("_")}

        if isinstance(value, (list, tuple)):
            return {str(index): item for index, item in enumerate(value)}

        raise TypeError(f"Unsupported event payload type: {type(value)!r}")

    @staticmethod
    def _parse_decimal(value: Any) -> Decimal:
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float)):
            return Decimal(str(value))
        if isinstance(value, str):
            return Decimal(value.strip())
        raise TypeError(f"Unsupported decimal value: {type(value)!r}")

    @staticmethod
    def _parse_float(value: Any) -> float:
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, str):
            return float(value.strip())
        raise TypeError(f"Unsupported float value: {type(value)!r}")

    @staticmethod
    def _parse_timestamp(value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None)
        if isinstance(value, str):
            try:
                return pendulum.parse(value.strip()).naive()
            except (TypeError, ValueError):
                return pendulum.parse(value.strip(), strict=False).naive()
        return value

    @classmethod
    def map(cls, value: Any) -> dict[str, Any]:
        data = cls._to_mapping(value)
        normalized: dict[str, Any] = {}

        for key, raw in data.items():
            if raw is None:
                normalized[key] = None
                continue

            key_name = str(key)
            value_to_normalize = raw

            if isinstance(value_to_normalize, str):
                stripped = value_to_normalize.strip()

                if key_name in cls._uppercase_fields:
                    normalized[key_name] = stripped.upper()
                    continue
                if key_name in cls._lowercase_fields:
                    normalized[key_name] = stripped.lower()
                    continue
                if key_name == "event_timestamp":
                    normalized[key_name] = cls._parse_timestamp(stripped)
                    continue
                if key_name in cls._decimal_fields:
                    normalized[key_name] = cls._parse_decimal(stripped)
                    continue
                if key_name in cls._float_fields:
                    normalized[key_name] = cls._parse_float(stripped)
                    continue
                normalized[key_name] = stripped
                continue

            if key_name in cls._decimal_fields:
                normalized[key_name] = cls._parse_decimal(value_to_normalize)
                continue
            if key_name in cls._float_fields:
                normalized[key_name] = cls._parse_float(value_to_normalize)
                continue
            if key_name == "event_timestamp":
                normalized[key_name] = cls._parse_timestamp(value_to_normalize)
                continue

            normalized[key_name] = value_to_normalize

        return normalized
