import time
from functools import wraps

from exchange.selector import get_exchange_client


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


@ttl_cache(ttl_seconds=86400)  # Cache for the specified timeframe
def cached_client():
    return get_exchange_client()
