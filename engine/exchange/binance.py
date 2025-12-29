import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
import ccxt # pyright: ignore[reportMissingImports]
from config.settings import is_demo_enabled as enable_demo

load_dotenv()

def create_client():
    api_key = os.getenv("API_KEY")
    api_secret = os.getenv("API_SECRET")

    client = ccxt.binance({
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
        "options": {
            "defaultType": "spot",
        }
    })


    client.enableDemoTrading(enable_demo) 

    return client

bi_client = create_client()