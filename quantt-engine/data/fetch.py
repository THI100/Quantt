import time
from typing import Optional

from data.client import cached_client

c_client = cached_client()


def get_ticker(symbol: str):
    """Fetch a ticker."""
    time.sleep(0.5)
    return c_client.fetch_ticker(symbol)


def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    time.sleep(0.5)
    return c_client.fetch_tickers(symbols)


def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    time.sleep(0.5)
    return c_client.fetch_ohlcv(symbol, timeframe, limit=limit)


def get_order_book(symbol: str, limit: Optional[int] = None):
    """Fetch the order book from a certain symbol."""
    time.sleep(0.5)
    return c_client.fetch_order_book(symbol, limit)


def get_order(symbol: str, id: str):
    """Fetch the order from a certain symbol."""
    time.sleep(0.5)
    return c_client.fetch_order(id, symbol)


def get_orders(symbol: str, limit: Optional[int] = None):
    time.sleep(0.5)
    return c_client.fetch_orders(symbol, limit=limit)


def get_open_orders(symbol: str, limit: Optional[int] = None):
    time.sleep(0.5)
    return c_client.fetch_open_orders(symbol, limit=limit)


def balance():
    time.sleep(0.5)
    return c_client.fetch_balance()
