import json
import logging
from decimal import Decimal
from logging import Logger
from typing import Any

import pendulum
from requests.exceptions import HTTPError

from src.common.keys import TXN_KEY, TXN_SLIDING_WINDOW_KEY

from src.config.settings import AppSettings
from src.contracts.score_events import BaseScoredEvents
from src.integrations.redis import RedisClient

class RedisSlidingWindow(RedisClient):
    def __init__(self, logger, settings):
        super().__init__(logger, settings)


    def set_data(
        self,
        
        score_result: ScoreResult
    ) -> None:

        timestamp = round(pendulum.parse(value.event_timestamp).timestamp(), 4)
    
        sliding_key = TXN_SLIDING_WINDOW_KEY.format(value.user_id)
        txn_key = TXN_KEY.format(transaction_id=value.transaction_id)

        self.conn.zadd(
            name=sliding_key,
            mapping={
                value.transaction_id : timestamp
            }
        )

        self.conn.set(
            name=txn_key,
            value=value.model_dump(),
        )

        return None

    def get_data(
        self, 
        user_id: str, 
        start: float | str, 
        end: float | str
    ):
        key = TXN_SLIDING_WINDOW_KEY.format(user_id)
        self.conn.zrangebyscore(
            name=key,
            min=start,
            max=end
        )