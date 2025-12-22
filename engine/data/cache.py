import data.fetch as fetch
from config import settings
import time
from functools import wraps
from utils import math


def ttl_cache(ttl_seconds: int):
    def decorator(func):
        cache = {"value": None, "expiry": 0}

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            if now >= cache["expiry"]:
                cache["value"] = func(*args, **kwargs)
                cache["expiry"] = now + ttl_seconds
            return cache["value"]

        return wrapper
    return decorator


@ttl_cache(ttl_seconds=math.get_cache_timing(settings.timeframe))  # Cache for the specified timeframe
def cached_p42(market: str):
    return fetch.get_OHLCV(
        symbol=market,
        timeframe=settings.timeframe,
        limit=42
    )

@ttl_cache(ttl_seconds=math.get_cache_timing(settings.timeframe))  # Cache for the specified timeframe
def cached_p14(market: str):
    return fetch.get_OHLCV(
        symbol=market,
        timeframe=settings.timeframe,
        limit=14
    )

@ttl_cache(ttl_seconds=math.get_cache_timing(settings.timeframe))  # Cache for the specified timeframe
def cached_p28(market: str):
    return fetch.get_OHLCV(
        symbol=market,
        timeframe=settings.timeframe,
        limit=28
    )