from redis.asyncio import Redis as AsyncRedis

from src.config.redis import settings as redis_settings

import atexit
import asyncio

redis = AsyncRedis.from_url(redis_settings.redis_url)


def redis_close():
    asyncio.run(redis.close())

atexit.register(redis_close)