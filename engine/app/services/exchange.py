# app/services/exchange.py
import os
from dotenv import load_dotenv
import ccxt
import time

load_dotenv()

def create_binance_client(testnet=True):
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    base_params = {
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
    }

    # Enable testnet mode
    if testnet:
        base_params["options"] = {
            "defaultType": "spot",
        }
        base_params["urls"] = {
            "api": {
                "public": "https://testnet.binance.vision/api",
                "private": "https://testnet.binance.vision/api",
            }
        }
    else:
        base_params["options"] = { "defaultType": "spot" }

    return ccxt.binance(base_params)

# Use testnet by default.
exchange = create_binance_client(testnet=True)

def get_ticker(symbol="BTC/USDT"):
    """
    Fetches ticker from testnet.
    Testnet supports fewer symbols; BTC/USDT works.
    """
    for attempt in range(3):
        try:
            return exchange.fetch_ticker(symbol)
        except ccxt.BaseError as e:
            last_err = e
            time.sleep(0.5 * (attempt + 1))
    raise last_err