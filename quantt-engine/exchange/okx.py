import os

import ccxt.async_support as ccxt
from dotenv import load_dotenv
from loguru import logger

from config.settings import FUTURE_SPOT

load_dotenv()


async def create_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        logger.error("Missing API credentials")

    client = ccxt.okx(
        {
            # SETTINGS, CURIOUS? YES, YOU CAN TWEAK ON IT.
            "apiKey": api_key,
            "secret": api_secret,
            # DONT MESS WITH THIS ONE!
            "enableRateLimit": True,
            "timeout": 30000,
            "throwOnError": True,
            "precisionMode": ccxt.TICK_SIZE,
            "options": {
                # NOT EVEN THAT ONE, FOR THE SAFETY OF THE ENGINE! :)
                "defaultType": FUTURE_SPOT,
                "adjustForTimeDifference": True,
                "recvWindow": 10000,
                "warnOnFetchOpenOrdersWithoutSymbol": False,
                "createMarketBuyOrderRequiresPrice": True,
            },
        }
    )

    return client
