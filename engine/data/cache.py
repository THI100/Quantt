import data.fetch as fetch
from config import settings
from config.markets import markets as tickers

cached_p42 = fetch.get_OHLCV(symbol="ETH/USDT", timeframe=settings.timeframe, limit=42)