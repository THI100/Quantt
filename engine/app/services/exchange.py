import os
from dotenv import load_dotenv
import ccxt
import time
import datetime

load_dotenv()

def create_binance_testnet_client():
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    client = ccxt.binance({
        "apiKey": api_key,
        "secret": api_secret,
        "enableRateLimit": True,
        "options": {
            "defaultType": "spot",
        }
    })

    # Use this instead of set_sandbox_mode=True and manual URL overrides
    client.enable_demo_trading(True) 

    # You may still want these options:
    client.options["warnOnFetchBalanceWithoutAddress"] = False
    client.options["recvWindow"] = 5000 

    return client

exchange = create_binance_testnet_client()


def get_OHLCV(symbol="BTC/USDT", timeframe="5m", limit=20):
    """Fetch a 20 OHLCV."""
    return exchange.fetchOHLCV(symbol, timeframe, limit = limit)

def get_ticker(symbol="BTC/USDT"):
    """Fetch a ticker."""
    return exchange.fetch_ticker(symbol)

