import asyncio
import os
import sys

import ccxt.async_support as ccxt
from loguru import logger

import core.engine as e
import data.fetch as fetch
from config import risk, settings
from exchange.binance import create_client

# Ensure your cached_client returns an ASYNC ccxt instance
# e.g., client = ccxt.async_support.binance({...})
from execution.position_manager import manage_open_limit
from persistance.connection import Base, engine


async def start():
    exchange = await create_client()
    try:
        # Load markets to ensure the symbol is recognized
        await exchange.load_markets()
        # Await the asynchronous fetch_ticker method
        ticker = await exchange.fetch_ticker("BTC/USDT")
        print(f"Price of {symbol} on {exchange}: {ticker['last']}")
    except Exception as e:
        print(f"Error fetching ticker from {exchange}: {e}")
    finally:
        # Crucial: explicitly close the exchange connection in async code
        await exchange.close()


#     try:
#         # CRITICAL: Must await the cached_client coroutine
#         client = await create_client()
#         # print(client.describe())

#         try:
#             print(await fetch.get_ticker("BTC/USDT"))
#         except Exception as e:
#             raise e
#         # Verify the client was actually returned
#         if client is None:
#             logger.error("Failed to initialize exchange client.")
#             return

#         # 2. Load Markets (API Fetch) - mandatory for CCXT calculation accuracy
#         logger.info("Loading exchange markets...")
#         for attempt in range(3):
#             try:
#                 await client.load_markets()
#                 logger.info("Successfully connected!")
#                 return client
#             except (ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as e:
#                 logger.debug(f"Attempt {attempt + 1} failed... retrying.")
#                 await asyncio.sleep(2)  # Give it a breather

#         # 3. Database setup (Sync is fine here as it's a one-off)
#         if not os.path.exists("./general.db"):
#             logger.info("Initializing new database...")
#             Base.metadata.create_all(bind=engine)

#         # 4. Set Leverage for all symbols in parallel
#         logger.info(f"Setting leverage to {risk.leverage}x...")
#         leverage_tasks = [
#             client.set_leverage(risk.leverage, symbol)
#             for symbol in settings.list_of_interest
#         ]
#         await asyncio.gather(*leverage_tasks)

#         # 5. Main Execution Loop
#         while True:
#             logger.debug("Running iteration...")

#             # NOTE: For maximum speed, manage_open_limit and e.avaliation_and_place
#             # should be defined as 'async def' and called with 'await'
#             await manage_open_limit(client)
#             await e.avaliation_and_place()

#             await asyncio.sleep(90)

#     except Exception as err:
#         logger.error(f"Bot encountered an error: {err}")


# if __name__ == "__main__":
#     try:
#         asyncio.run(start())
#     except KeyboardInterrupt:
#         pass
