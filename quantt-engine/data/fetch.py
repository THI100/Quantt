from typing import Optional

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
    return c_client.fetch_ohlcv(symbol, timeframe, limit=limit)


def get_order_book(symbol: str, limit: Optional[int] = None):
    """Fetch the order book from a certain symbol."""
    return c_client.fetch_order_book(symbol, limit)


def get_order(symbol: str, id: str):
    """Fetch the order from a certain symbol."""
    return c_client.fetch_order(id, symbol)


def get_orders(symbol: str, limit: Optional[int] = None):
    return c_client.fetch_orders(symbol, limit=limit)


def balance():
    return c_client.fetch_balance()
