from functools import lru_cache
import redis.asyncio as redis
from .config import get_settings


@lru_cache()
def get_redis():
    settings = get_settings()
    return redis.from_url(settings.redis_url)


async def get_cache():
    return get_redis()