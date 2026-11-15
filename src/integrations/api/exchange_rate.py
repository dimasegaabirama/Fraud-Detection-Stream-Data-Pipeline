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
from src.integrations.redis import RedisClient


class ExchangeAPI:

    def __init__(self, logger, settings, redis_client: RedisClient):
        self.logger = logger or logging.getLogger(__name__)
        self.settings = settings
        self.client = redis_client

        self.api_settings = settings.api.get(API_EXCHANGE_RATE_NAME)
        if self.api_settings is None:
            raise ValueError(f"API config for {API_EXCHANGE_RATE_NAME} is not found!")

        self.base_currency = self.api_settings.base_currency

    @staticmethod
    def _parse_currency_data(data: bytes | str, currency: str) -> dict[str, Any]:
        payload = json.loads(data, parse_float=Decimal)
        return payload[currency]

    def get_rates(self) -> dict[str, Any]:
        cache_key = API_EXCHANGE_RATE_KEY.format(currency=self.base_currency)
        urls = self.api_settings.full_urls

        cached_data = self.client.get_data(cache_key)
        if cached_data:
            self.logger.debug(f"Using cached exchange rates for {self.base_currency}")
            return self._parse_currency_data(cached_data, self.base_currency)

        for url in urls:
            try:
                response = requests.get(url)
                response.raise_for_status()
                self.client.set_data(
                    key=cache_key,
                    value=response.content,
                    px=self.api_settings.refresh_ms,
                )
                return self._parse_currency_data(response.content, self.base_currency)
            except HTTPError:
                self.logger.warning("Exchange-rate request failed; trying the alternate URL")
                continue
            except Exception as error:
                raise ValueError("Failed to fetch exchange-rate data") from error

        raise ValueError(f"Failed to fetch exchange-rate data for {self.base_currency}")

    def get_currency_rate(self, currency: str) -> Decimal:
        exchange_rate = self.get_rates().get(currency)
        if exchange_rate is None:
            raise ValueError(
                f"Currency rate from {self.base_currency} to {currency} not found"
            )
        return exchange_rate

    def convert_to_base_currency(self, currency: str, value: Decimal) -> Decimal:
        rate = self.get_currency_rate(currency)
        return value / rate
        

if __name__ == "__main__":
    logger = logging.getLogger(__name__).setLevel("DEBUG")
    settings = AppSettings()
    exchange_api = ExchangeAPI(logger=logger, settings=settings)
    

