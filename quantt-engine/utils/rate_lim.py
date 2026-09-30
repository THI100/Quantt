import threading
import time


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
