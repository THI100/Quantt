from exchange import c_client
from config import settings

def get_OHLCV(symbol="BTC/USDT", timeframe="5m", limit=20):
    """Fetch a 20 OHLCV."""
    return c_client.fetchOHLCV(symbol, timeframe, limit = limit)

def get_ticker(symbol="BTC/USDT"):
    """Fetch a ticker."""
    return c_client.fetch_tickers(symbol)