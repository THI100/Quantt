import fetch
from config import settings
from config.markets import markets as tickers
import fetch

cached_p42 = {
    fetch.get_OHLCV(
    """Cached 42 candles for indicators""",

    symbol=tickers[1],
    timeframe=settings.timeframe,
    limit=42,
)
} 