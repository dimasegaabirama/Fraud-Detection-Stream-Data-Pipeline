import json
import logging
from decimal import Decimal
from logging import Logger
from typing import Any

import requests
from requests.exceptions import HTTPError

from src.common.names import API_EXCHANGE_RATE_NAME
from src.common.keys import API_EXCHANGE_RATE_KEY

from src.config.settings import AppSettings
from src.integrations import RedisConn


class ExchangeAPI:
    def __init__(self, settings: AppSettings, redis_conn: RedisConn, logger: Logger | None = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.redis_conn = redis_conn

        self.settings = settings.api.get(API_EXCHANGE_RATE_NAME)
        if self.settings is None:
            raise ValueError(f"API config for {API_EXCHANGE_RATE_NAME} is not found!")

    @staticmethod
    def _parse_currency_data(data: bytes | str, currency: str) -> dict[str, Any]:
        payload = json.loads(data, parse_float=Decimal)
        return payload[currency]

    def get_currency(self) -> dict[str, Any]:
        cache_key = API_EXCHANGE_RATE_KEY.format(self.settings.base_currency)
        urls = self.settings.urls

        cached_data = self.redis_conn.get_cache(cache_key)
        if cached_data:
            self.logger.debug(f"Using cached exchange rates for {self.settings.base_currency}")
            return self._parse_currency_data(cached_data, self.settings.base_currency)

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                self.redis_conn.set_cache(
                    key=cache_key,
                    value=response.content,
                    px=self.settings.ttl_ms,
                )
                return self._parse_currency_data(response.content, self.settings.base_currency)
            except HTTPError:
                self.logger.warning("Exchange-rate request failed; trying the alternate URL")
                continue
            except Exception as error:
                raise ValueError("Failed to fetch exchange-rate data") from error

        raise ValueError(f"Failed to fetch exchange-rate data for {self.settings.base_currency}")

    def get_rate(self, currency: str) -> Decimal:
        exchange_rate = self.get_currency().get(self.settings.base_currency)
        if exchange_rate is None:
            raise ValueError(
                f"Currency rate from {self.settings.base_currency} to {currency} not found"
            )
        return exchange_rate