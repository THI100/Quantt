import asyncio
import time
from functools import wraps

import data.fetch as fetch
from config import settings
from utils import math


def ttl_cache(ttl_seconds: int):
    def decorator(func):
        cache = {}
        lock = asyncio.Lock()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = (args, frozenset(kwargs.items()))

            async with lock:
                now = time.time()
                cached_item = cache.get(cache_key)

                if cached_item is None or now >= cached_item["expiry"]:
                    result = await func(*args, **kwargs)
                    cache[cache_key] = {"value": result, "expiry": now + ttl_seconds}

            return cache[cache_key]["value"]

        return wrapper

    return decorator


@ttl_cache(ttl_seconds=math.get_cache_timing(settings.timeframe))
async def cached_p42(market: str):
    return await fetch.get_OHLCV(symbol=market, timeframe=settings.timeframe, limit=42)


@ttl_cache(ttl_seconds=math.get_cache_timing(settings.timeframe))
async def cached_p14(market: str):
    return await fetch.get_OHLCV(symbol=market, timeframe=settings.timeframe, limit=14)


@ttl_cache(ttl_seconds=math.get_cache_timing(settings.timeframe))
async def cached_p28(market: str):
    return await fetch.get_OHLCV(symbol=market, timeframe=settings.timeframe, limit=28)
