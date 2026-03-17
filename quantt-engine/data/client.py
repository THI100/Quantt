import asyncio
import time
from functools import wraps

from exchange.selector import get_exchange_client


# TTL CACHE, YES FOR A EXCHANGE SETUP!
def async_ttl_cache(ttl_seconds: int):
    def decorator(func):
        cache = {"value": None, "expiry": 0}
        lock = asyncio.Lock()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with lock:
                now = time.time()
                if now >= cache["expiry"]:
                    # AWAIT FOR THAT
                    cache["value"] = await func(*args, **kwargs)
                    cache["expiry"] = now + ttl_seconds
            return cache["value"]

        return wrapper

    return decorator


@async_ttl_cache(ttl_seconds=86400)
async def cached_client():
    # NOW IT MAYBE IS ASYNC, I DONT KNOW
    return get_exchange_client()
