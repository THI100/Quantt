from loguru import logger

from config import settings


async def get_exchange_client(exchange_name: str = settings.EXCHANGE):
    try:
        if exchange_name == "bybit":
            from exchange.bybit import create_client

            # CRITICAL: Added () to actually call the function
            client = await create_client()
            return client

        elif exchange_name == "binance":
            from exchange.binance import create_client

            client = await create_client()
            return client

        elif exchange_name == "okx":
            from exchange.okx import create_client

            client = await create_client()
            return client

        else:
            logger.error(f"Unsupported exchange: {exchange_name}")
            return None

    except Exception as e:
        logger.error(f"Failed to initialize {exchange_name}: {e}")
        return None
