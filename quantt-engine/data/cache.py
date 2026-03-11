import time
from functools import wraps

import data.fetch as fetch
from config import settings
from utils import math


def ttl_cache(ttl_seconds: int):
    def decorator(func):
        # Store data as: { (args, kwargs): {"value": result, "expiry": time} }
        cache = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique key based on the function arguments
            # Note: args must be hashable (like strings or tuples)
            cache_key = (args, frozenset(kwargs.items()))

            now = time.time()
            cached_item = cache.get(cache_key)

            if cached_item is None or now >= cached_item["expiry"]:
                # Fetch new data and update the specific key
                result = func(*args, **kwargs)
                cache[cache_key] = {"value": result, "expiry": now + ttl_seconds}

            return cache[cache_key]["value"]

        return wrapper

    return decorator


@ttl_cache(
    ttl_seconds=math.get_cache_timing(settings.timeframe)
)  # Cache for the specified timeframe
def cached_p42(market: str):
    return fetch.get_OHLCV(symbol=market, timeframe=settings.timeframe, limit=42)


@ttl_cache(
    ttl_seconds=math.get_cache_timing(settings.timeframe)
)  # Cache for the specified timeframe
def cached_p14(market: str):
    return fetch.get_OHLCV(symbol=market, timeframe=settings.timeframe, limit=14)


@ttl_cache(
    ttl_seconds=math.get_cache_timing(settings.timeframe)
)  # Cache for the specified timeframe
def cached_p28(market: str):
    return fetch.get_OHLCV(symbol=market, timeframe=settings.timeframe, limit=28)
