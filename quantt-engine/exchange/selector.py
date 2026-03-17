from loguru import logger

from config import settings


async def get_exchange_client(exchange_name: str = settings.EXCHANGE):
    if exchange_name == "bybit":
        from exchange.bybit import create_client

        client = await create_client
        return client

    elif exchange_name == "binance":
        from exchange.binance import create_client

        client = await create_client
        return client

    elif exchange_name == "okx":
        from exchange.okx import create_client

        client = await create_client
        return client

    else:
        logger.error(f"Unsupported exchange: {exchange_name}")
