import os

import ccxt.async_support as ccxt
from dotenv import load_dotenv
from loguru import logger

from config.settings import FUTURE_SPOT, is_demo_enabled

load_dotenv()


async def create_client():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    # Use the renamed import here
    client = ccxt.binance(
        {
            "apiKey": api_key,
            "secret": api_secret,
            "enableRateLimit": True,
            "options": {
                "defaultType": "future",
            },
        }
    )

    # Ensure is_demo_enabled is actually a Boolean (True/False)
    client.enable_demo_trading(bool(is_demo_enabled))

    return client
