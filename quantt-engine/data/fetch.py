from typing import Optional

from data.client import cached_client


async def get_ticker(symbol: str):
    """Fetch a ticker."""
    client = await cached_client()
    return await client.fetch_ticker(symbol)


async def get_tickers(symbols: list):
    """Fetch multiple tickers."""
    client = await cached_client()
    return await client.fetch_tickers(symbols)


async def get_OHLCV(symbol: str, timeframe: str, limit: int):
    """Fetch a x amount of OHLCV from x market wih x timeframe."""
    client = await cached_client()
    return await client.fetch_ohlcv(symbol, timeframe, limit=limit)


async def get_order_book(symbol: str, limit: Optional[int] = None):
    """Fetch the order book from a certain symbol."""
    client = await cached_client()
    return await client.fetch_order_book(symbol, limit)


async def get_order(symbol: str, id: str):
    """Fetch the order from a certain symbol."""
    client = await cached_client()
    return await client.fetch_order(id, symbol)


async def get_orders(symbol: str, limit: Optional[int] = None):
    client = await cached_client()
    return await client.fetch_orders(symbol, limit=limit)


async def get_open_orders(symbol: str, limit: Optional[int] = None):
    client = await cached_client()
    return await client.fetch_open_orders(symbol, limit=limit)


async def balance():
    client = await cached_client()
    return await client.fetch_balance()
