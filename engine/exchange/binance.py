import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
import ccxt # pyright: ignore[reportMissingImports]

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


    client.enableDemoTrading(True) 

    # You may still want these options:
    client.options["warnOnFetchBalanceWithoutAddress"] = False
    client.options["recvWindow"] = 5000 

    return client

c_client = create_binance_testnet_client()