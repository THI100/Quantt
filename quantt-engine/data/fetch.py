from typing import Optional

from loguru import logger

from data.client import cached_client
from utils.rate_lim import std_call


def get_ticker(symbol: str):
    """Fetch a ticker."""
    try:
        client = cached_client()

        return std_call(client.fetch_ticker, symbol)

    except Exception as err:
        logger.error(f"following cause the ticker fetch to fail: {err}")


def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    try:
        client = cached_client()

        return std_call(client.fetch_tickers, symbols)

    except Exception as err:
        logger.error(f"following cause the tickers fetch to fail: {err}")


def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    try:
        client = cached_client()

        return std_call(client.fetch_ohlcv, symbol, timeframe, limit)

    except Exception as err:
        logger.error(f"following cause the OHLCV fetch to fail: {err}")


def get_order_book(symbol: str, limit: Optional[int] = None):
    """Fetch the order book from a certain symbol."""
    try:
        client = cached_client()

        return std_call(client.fetch_order_book, symbol, limit)

    except Exception as err:
        logger.error(f"following cause the order book fetch to fail: {err}")


def get_order(symbol: str, id: str):
    """Fetch the order from a certain symbol."""
    try:
        client = cached_client()

        return std_call(client.fetch_order, id, symbol)

    except Exception as err:
        logger.error(f"following cause the order fetch to fail: {err}")


def get_orders(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()

        return std_call(client.fetch_orders, symbol, limit)

    except Exception as err:
        logger.error(f"following cause the orders fetch to fail: {err}")


def get_open_orders(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()

        return std_call(client.fetch_open_orders, symbol, limit)

    except Exception as err:
        logger.error(f"following cause the open orders fetch to fail: {err}")


def balance():
    try:
        client = cached_client()

        return std_call(client.fetch_balance)

    except Exception as err:
        logger.error(f"following cause the balance fetch to fail: {err}")
