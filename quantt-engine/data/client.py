import time
from functools import wraps

from exchange.selector import get_exchange_client


def ttl_cache(ttl_seconds: int):
    def decorator(func):
        cache = {"value": None, "expiry": 0}

        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()

            # recreate if expired
            if cache["value"] is None or now >= cache["expiry"]:
                cache["value"] = func(*args, **kwargs)
                cache["expiry"] = now + ttl_seconds

            return cache["value"]

        def reset():
            cache["value"] = None
            cache["expiry"] = 0

        wrapper.reset = reset

        return wrapper

    return decorator


@ttl_cache(ttl_seconds=86399)  # Cache for the specified timeframe
def cached_client():
    return get_exchange_client()
