from decimal import Decimal

import pytest
from requests.exceptions import HTTPError

from src.integrations.api.exchange_rate import ExchangeAPI


def test_get_currency_returns_cached_rates_as_decimals(mocker) -> None:
    redis_conn = mocker.Mock()
    redis_conn.get_cache.return_value = b'{"idr":{"usd":0.00006}}'
    exchange_api = ExchangeAPI(redis_conn)
    get_request = mocker.patch("src.integrations.api.exchange_rate.requests.get")
    rates = exchange_api.get_currency("idr")

    assert rates["usd"] == Decimal("0.00006")
    get_request.assert_not_called()


def test_get_currency_tries_alternate_url_after_http_error(mocker) -> None:
    redis_conn = mocker.Mock()
    redis_conn.get_cache.return_value = None
    exchange_api = ExchangeAPI(redis_conn)
    failed_response = mocker.Mock()
    failed_response.raise_for_status.side_effect = HTTPError("not found")
    successful_response = mocker.Mock()
    successful_response.content = b'{"idr":{"usd":0.00006}}'
    get_request = mocker.patch(
        "src.integrations.api.exchange_rate.requests.get",
        side_effect=[failed_response, successful_response],
    )
    rates = exchange_api.get_currency("idr")

    assert rates["usd"] == Decimal("0.00006")
    assert get_request.call_count == 2
    redis_conn.set_cache.assert_called_once_with(
        key="api:exchage:idr",
        value=successful_response.content,
        ex=exchange_api.ttl,
    )


def test_get_exchange_rate_reports_missing_exchange_currency(mocker) -> None:
    redis_conn = mocker.Mock()
    redis_conn.get_cache.return_value = b'{"idr":{}}'
    exchange_api = ExchangeAPI(redis_conn)

    with pytest.raises(ValueError, match="usd.*idr"):
        exchange_api.get_exchange_rate("idr", "usd")