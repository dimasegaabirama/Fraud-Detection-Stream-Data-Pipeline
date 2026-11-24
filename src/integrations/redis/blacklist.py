import json
import logging
from decimal import Decimal
from logging import Logger
from typing import Any

import pendulum
from requests.exceptions import HTTPError

from src.common.keys import TXN_BLACKLIST_KEY
from src.models.enums import BlacklistType

from src.config.settings import AppSettings
from src.integrations.redis import RedisClient

class BlacklistClient(RedisClient):
    def __init__(self, logger, settings):
        super().__init__(logger, settings)

    def set_data(
        self,
        blacklist_type: BlacklistType,
        value: str,
        expire_ms: int | None
    ) -> list[Any]:
        blacklist_key = TXN_BLACKLIST_KEY.format(type=blacklist_type)
        try:
            pipe = self.conn.pipeline()
            pipe.set(
                name=blacklist_key,
                value=value,
                px=expire_ms
            )

            return pipe.execute()
        except Exception as e:
            raise RuntimeError("Error to set redis data") from e

    def get_data(
        self,
        blacklist_type: BlacklistType
    ) -> list[Any]:
        blacklist_key = TXN_BLACKLIST_KEY.format(type=blacklist_type)
        try:
            pipe = self.conn.pipeline()
            pipe.get(blacklist_key)
            return pipe.execute()
        except Exception as e:
            raise RuntimeError("Error to get redis data") from e

    def is_ip_address_blacklist(
            self,
            ip_address: str
    ) -> bool:
        ip_address_list = self.get_data(blacklist_type=BlacklistType.IP_ADDRESS)
        return ip_address in ip_address_list

    def is_user_id_blacklist(
            self,
            user_id: str
    ) -> bool:
        user_id_list = self.get_data(blacklist_type=BlacklistType.USER_ID)
        return user_id in user_id_list



if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    settings = AppSettings()


