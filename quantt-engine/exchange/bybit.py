import os
from dotenv import load_dotenv
import ccxt
from config.settings import is_demo_enabled as enable_demo

load_dotenv()

def create_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    if not api_key or not api_secret:
        raise RuntimeError("Missing API credentials")

    client = ccxt.bybit({
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
    })

    # Correct, modern CCXT usage
    client.enableDemoTrading(enable_demo)

    return client

bb_client = create_client()