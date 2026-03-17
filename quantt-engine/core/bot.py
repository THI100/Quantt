import asyncio
import os

from loguru import logger

import core.engine as e
from config import risk, settings

# Ensure your cached_client returns an ASYNC ccxt instance
# e.g., client = ccxt.async_support.binance({...})
from data.client import cached_client
from execution.position_manager import manage_open_limit
from persistance.connection import Base, engine


async def start():
    # 1. Initialize the Async Client
    client = cached_client()

    try:
        # 2. Load Markets (API Fetch) - mandatory for CCXT calculation accuracy
        logger.info("Loading exchange markets...")
        await client.load_markets()

        # 3. Database setup (Sync is fine here as it's a one-off)
        if not os.path.exists("./general.db"):
            logger.info("Initializing new database...")
            Base.metadata.create_all(bind=engine)

        # 4. Set Leverage for all symbols in parallel
        logger.info(f"Setting leverage to {risk.leverage}x...")
        leverage_tasks = [
            client.set_leverage(risk.leverage, symbol)
            for symbol in settings.list_of_interest
        ]
        await asyncio.gather(*leverage_tasks)

        # 5. Main Execution Loop
        while True:
            logger.debug("Running iteration...")

            # NOTE: For maximum speed, manage_open_limit and e.avaliation_and_place
            # should be defined as 'async def' and called with 'await'
            await manage_open_limit(client)
            await e.avaliation_and_place()

            await asyncio.sleep(90)

    except Exception as err:
        logger.error(f"Bot encountered an error: {err}")
    finally:
        # 6. Graceful Shutdown: Close the aiohttp connectors inside CCXT
        await client.close()
        logger.info("Exchange connection closed. Bot stopped.")


if __name__ == "__main__":
    try:
        asyncio.run(start())
    except KeyboardInterrupt:
        pass
