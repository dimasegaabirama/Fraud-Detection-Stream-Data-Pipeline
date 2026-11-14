import logging
from logging import Logger
from contextlib import contextmanager
from typing import Any

import redis
from redis.connection import ConnectionPool

from src.config.settings import AppSettings


class RedisConn:
    _pool = None

    def __init__(self, logger: Logger, settings: AppSettings):
        self.logger = logger or logging.getLogger(__name__)
        if not RedisConn._pool:
            RedisConn._pool = ConnectionPool(**settings.redis.model_dump())

        self.conn = redis.Redis(connection_pool=self._pool)

    def get_cache(self, key) -> Any | None:
        return self.conn.get(key)

    def set_cache(
        self,
        key: Any,
        value: Any,
        ex: Any | None = None,
        px: Any | None = None,
        nx: bool = False,
        xx: bool = False,
        keepttl: bool = False,
    ) -> Any | None:
        return self.conn.set(key, value, ex=ex, px=px, nx=nx, xx=xx, keepttl=keepttl)

    @contextmanager
    def redis_session(self):
        try:
            yield self.conn
        except Exception:
            raise
        finally:
            self.conn.close()
