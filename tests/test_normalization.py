import pytest
from pyflink.common import Row

from src.application.transform.helpers.normalization import NormalizeTransaction
from src.config.settings import AppSettings


@pytest.mark.parametrize("as_row", [False, True])
def test_normalize_transaction_accepts_mapping_and_flink_row(as_row: bool) -> None:
    values = {
        "event_id": "evt-001",
        "transaction_id": "txn-001",
        "user_id": "user-001",
        "amount": "125.50",
        "currency": " idr ",
        "segment": " RETAIL ",
        "transaction_type": " TRANSFER ",
        "direction": " OUT ",
        "device_type": " IOS ",
        "status": " SUCCESS ",
        "ip_address": "192.0.2.1",
        "device_id": "device-001",
        "latitude": "-6.2",
        "longitude": "106.8",
        "event_timestamp": "2026-02-01T10:00:00",
    }
    event = Row(**values) if as_row else values

    normalized = NormalizeTransaction(AppSettings()).map(event)

    assert normalized["currency"] == "IDR"
    assert normalized["segment"] == "retail"
    assert normalized["transaction_type"] == "transfer"
    assert normalized["direction"] == "out"
    assert normalized["device_type"] == "ios"
    assert normalized["status"] == "success"
    assert normalized["latitude"] == -6.2
    assert normalized["longitude"] == 106.8
    assert normalized["event_timestamp"].tzinfo is None