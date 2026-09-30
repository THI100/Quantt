import threading
import time

import ccxt
from loguru import logger


class RateLimiter:
    def __init__(self, interval: float = 1.1):
        self.interval = interval
        self._last_request = 0.0
        self._lock = threading.Lock()

    def wait(self) -> None:
        with self._lock:
            now = time.monotonic()
            elapsed = now - self._last_request

            if elapsed < self.interval:
                time.sleep(self.interval - elapsed)

            self._last_request = time.monotonic()


gen_limiter = RateLimiter()


def std_call(func, *args, **kwargs):
    gen_limiter.wait()

    try:
        return func(*args, **kwargs)

    except ccxt.RateLimitExceeded:
        logger.warning("CCXT rate limit exceeded")
        raise

    except (ccxt.NetworkError, ccxt.ExchangeError) as err:
        logger.warning(f"CCXT error: {err}")
        raise
