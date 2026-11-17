import json
import logging
from decimal import Decimal
from logging import Logger
from typing import Any

import pendulum
from requests.exceptions import HTTPError

from src.common.keys import TXN_KEY, TXN_SLIDING_WINDOW_KEY
from src.contracts.cleaned_events import CleanedTransaction

from src.config.settings import AppSettings
from src.integrations.redis import RedisClient

class RedisSlidingWindow(RedisClient):
    def __init__(self, logger, settings):
        super().__init__(logger, settings)

    def set_data(
        self,
        value: CleanedTransaction
    ) -> list[Any]:
        sliding_key = TXN_SLIDING_WINDOW_KEY.format(user_id=value.user_id)
        txn_key = TXN_KEY.format(transaction_id=value.transaction_id)

        try:
            pipe = self.conn.pipeline()
            unix_timestamp = round(pendulum.parse(value.event_timestamp).timestamp(), 4)

            pipe.zadd(
                name=sliding_key,
                mapping={
                    value.transaction_id : unix_timestamp
                }
            )

            pipe.set(
                name=txn_key,
                value=str(value.model_dump()),
            )
            
            return pipe.execute()
        except Exception as e:
            raise RuntimeError("Error to set redis data") from e

    def get_data(
        self,
        user_id: str,
        start: float | str,
        end: float | str,
        offset: int | None = None,
        num: int | None = None,
    ) -> list[Any]:
        sliding_key = TXN_SLIDING_WINDOW_KEY.format(user_id=user_id)

        try:
            txn_ids = self.conn.zrangebyscore(
                name=sliding_key,
                min=start,
                max=end,
                start=offset,
                num=num,
            )

            if not txn_ids:
                return []

            pipe = self.conn.pipeline()
            for txn_id in txn_ids:
                txn_key = TXN_KEY.format(transaction_id=txn_id)
                pipe.get(txn_key)

            return pipe.execute()
        except Exception as e:
            raise RuntimeError("Error to get redis data") from e



if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    settings = AppSettings()
    
    redis_sliding = RedisSlidingWindow(
        logger=logger,
        settings=settings
    )

    data = CleanedTransaction(
        event_id="evt_0004", transaction_id="trx_100004", user_id="usr_504",
        amount=Decimal("25000000.00"), currency="IDR",
        segment="business", transaction_type="transfer", direction="in",
        sender_account="9988776655", receiver_account="1122334455", merchant_id=None,
        ip_address="182.253.64.12", device_id="dev_g7h8i9", device_type="web",
        latitude=-6.9175, longitude=107.6191,
        status="reserved",
        event_timestamp="2026-11-16 13:20:30", processed_timestamp="2026-11-16 13:20:33"
    )

    print(redis_sliding.get_data(data.user_id, "-inf", "+inf"))
