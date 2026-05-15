import time
from typing import Optional

from loguru import logger

from data.client import cached_client


def get_ticker(symbol: str):
    """Fetch a ticker."""
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_ticker(symbol)
    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_ticker(symbol)


def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_tickers(symbols)
    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_tickers(symbols)


def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_ohlcv(symbol, timeframe, limit=limit)

    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_ohlcv(symbol, timeframe, limit=limit)


def get_order_book(symbol: str, limit: Optional[int] = None):
    """Fetch the order book from a certain symbol."""
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_order_book(symbol, limit)

    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_order_book(symbol, limit)


def get_order(symbol: str, id: str):
    """Fetch the order from a certain symbol."""
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_order(id, symbol)

    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_order(id, symbol)


def get_orders(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_orders(symbol, limit=limit)

    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_ticker(symbol, limit=limit)


def get_open_orders(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_open_orders(symbol, limit=limit)

    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_open_orders(symbol, limit=limit)


def balance():
    try:
        client = cached_client()
        time.sleep(0.5)
        return client.fetch_balance()

    except Exception as err:
        logger.warning(
            f"following cause triggered recreation of client instance: {err}"
        )
        cached_client.reset()

        client = cached_client()
        time.sleep(0.5)
        return client.fetch_balance()
