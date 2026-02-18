from data.client import cached_client

c_client = cached_client()


def get_ticker(symbol: str):
    """Fetch a ticker."""
    return c_client.fetch_ticker(symbol)


def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    return c_client.fetch_tickers(symbols)


def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    return c_client.fetchOHLCV(symbol, timeframe, limit=limit)


def get_balance():
    """Fetch account balance."""
    return c_client.fetch_balance()
