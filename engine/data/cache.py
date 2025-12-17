import data.fetch as fetch
from config import settings
from config.markets import markets as tickers
import time
from functools import wraps

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


@ttl_cache(ttl_seconds=900)  # Cache for 15 minutes
def cached_p42():
    return fetch.get_OHLCV(
        symbol="BTC/USDT",
        timeframe=settings.timeframe,
        limit=42
    )
