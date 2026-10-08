import itertools
from typing import Optional

from loguru import logger

from data.client import cached_client
from utils.rate_lim import std_call


def get_ticker(symbol: str):
    """Fetch a ticker."""
    try:
        client = cached_client()

        return std_call(client.fetch_ticker, symbol=symbol)

    except Exception as err:
        logger.error(f"following cause the ticker fetch to fail: {err}")


def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    try:
        client = cached_client()

        return std_call(client.fetch_tickers, symbols=symbols)

    except Exception as err:
        logger.error(f"following cause the tickers fetch to fail: {err}")


def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    try:
        client = cached_client()

        return std_call(
            client.fetch_ohlcv, symbol=symbol, timeframe=timeframe, limit=limit
        )

    except Exception as err:
        logger.error(f"following cause the OHLCV fetch to fail: {err}")


def get_order_book(symbol: str, limit: Optional[int] = None):
    """Fetch the order book from a certain symbol."""
    try:
        client = cached_client()

        return std_call(client.fetch_order_book, symbol=symbol, limit=limit)

    except Exception as err:
        logger.error(f"following cause the order book fetch to fail: {err}")


def get_order(symbol: str, id: str):
    """Fetch the order from a certain symbol."""
    try:
        client = cached_client()

        return std_call(client.fetch_order, id=id, symbol=symbol)

    except Exception as err:
        logger.error(f"following cause the order fetch to fail: {err}")


def get_orders(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()

        main = std_call(client.fetch_orders, symbol=symbol, limit=limit)

        try:
            canceled = std_call(
                client.fetch_canceled_orders, symbol=symbol, limit=limit
            )
        except Exception as e:
            logger.debug(f"Endpoint not supported or failed: {e}")
            canceled = []

        try:
            cc = std_call(
                client.fetch_canceled_and_closed_orders, symbol=symbol, limit=limit
            )
        except Exception as e:
            logger.debug(f"Endpoint not supported or failed: {e}")
            cc = []

        iterador = itertools.chain(main, canceled, cc)

        final = list({order.get("id"): order for order in iterador}.values())

        return final

    except Exception as err:
        logger.error(f"following cause the orders fetch to fail: {err}")


def get_generalized(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()

        open = std_call(client.fetch_open_orders, symbol=symbol, limit=limit)
        canceled = std_call(client.fetch_canceled_orders, symbol=symbol, limit=limit)
        closed = std_call(client.fetch_closed_orders, symbol=symbol, limit=limit)
        cc = std_call(
            client.fetch_canceled_and_closed_orders, symbol=symbol, limit=limit
        )

        # Chain all iterables together
        iterador = itertools.chain(open, canceled, closed, cc)

        # Deduplicate based on 'id' while keeping insertion order
        final = list({order.get("id"): order for order in iterador}.values())

        return final

    except Exception as err:
        logger.error(f"following cause the orders fetch to fail: {err}")


def get_open_orders(symbol: str, limit: Optional[int] = None):
    try:
        client = cached_client()

        return std_call(client.fetch_open_orders, symbol=symbol, limit=limit)

    except Exception as err:
        logger.error(f"following cause the open orders fetch to fail: {err}")


def balance():
    try:
        client = cached_client()

        return std_call(client.fetch_balance)

    except Exception as err:
        logger.error(f"following cause the balance fetch to fail: {err}")
