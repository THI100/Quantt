import os

import ccxt.async_support as ccxt  # type: ignore
from dotenv import load_dotenv
from loguru import logger

from config.settings import FUTURE_SPOT, is_demo_enabled

load_dotenv()


async def create_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        logger.error("Missing API credentials in environment variables.")
        return None

    # We initialize the async class
    client = ccxt.bybit(
        {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "timeout": 30000,
            "throwOnError": True,
            # If TICK_SIZE gives you an error,
            # you can use the integer value 4 or just omit it for Bybit default
            "precisionMode": ccxt.TICK_SIZE,
            "options": {
                "defaultType": FUTURE_SPOT,
                "adjustForTimeDifference": True,
                "recvWindow": 10000,
                "warnOnFetchOpenOrdersWithoutSymbol": False,
                "createMarketBuyOrderRequiresPrice": True,
            },
        }
    )

    if is_demo_enabled:
        client.set_sandbox_mode(True)
        logger.info("Sandbox/Demo mode enabled for Bybit.")

    return client
