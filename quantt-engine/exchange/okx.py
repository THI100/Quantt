import os

import ccxt
from dotenv import load_dotenv
from loguru import logger

from exchange.awm import ENV_PATH


def create_client():
    load_dotenv(dotenv_path=ENV_PATH, override=True)

    api_key = os.getenv("API_KEY_OKX")
    api_secret = os.getenv("API_SECRET_OKX")

    if not api_key or not api_secret:
        logger.error("Missing API credentials")

    client = ccxt.okx(
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
                "adjustForTimeDifference": True,
                "recvWindow": 10000,
                "warnOnFetchOpenOrdersWithoutSymbol": False,
                "createMarketBuyOrderRequiresPrice": True,
            },
        }
    )

    return client


okx_client = create_client()
