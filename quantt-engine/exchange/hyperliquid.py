import os

import ccxt
from dotenv import load_dotenv
from loguru import logger

from config import settings
from exchange.awm import ENV_PATH
from utils.rate_lim import std_call


def create_client():
    load_dotenv(dotenv_path=ENV_PATH, override=True)

    demo_enabled = settings.watcher.get_config().is_demo_enabled

    if demo_enabled:
        api_key = os.getenv("API_KEY_HYPERLIQUID_DEMO")
        api_secret = os.getenv("API_SECRET_HYPERLIQUID_DEMO")
    else:
        api_key = os.getenv("API_KEY_HYPERLIQUID")
        api_secret = os.getenv("API_SECRET_HYPERLIQUID")

    if not api_key or not api_secret:
        logger.error("Missing API credentials")

    client = ccxt.hyperliquid(
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
                "defaultType": settings.watcher.get_config().future_spot,
                "adjustForTimeDifference": True,
                "recvWindow": 10000,
                "warnOnFetchOpenOrdersWithoutSymbol": False,
                "createMarketBuyOrderRequiresPrice": True,
            },
        }
    )

    std_call(client.enable_demo_trading, enable=demo_enabled)

    return client


hl_client = create_client()
