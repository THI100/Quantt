from exchange.binance import c_client

def get_ticker(symbol: str):
    """Fetch a ticker."""
    return c_client.fetch_tickers(symbol)

def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    return c_client.fetch_tickers(symbols)

def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    return c_client.fetchOHLCV(symbol, timeframe, limit = limit)