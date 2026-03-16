import os

import ccxt
from dotenv import load_dotenv
from loguru import logger

from config.settings import FUTURE_SPOT, is_demo_enabled

load_dotenv()


def create_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        logger.error("Missing API credentials")

    client = ccxt.binance(
        {
            "apiKey": api_key,
            "secret": api_secret,
            # Stability
            "enableRateLimit": True,
            "timeout": 30000,
            "throwOnError": True,
            # Precision safety
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

    client.enable_demo_trading(is_demo_enabled)

    return client


bi_client = create_client()
