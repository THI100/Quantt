import os
import time
from typing import Optional

from loguru import logger

import core.engine as e
from config import risk, settings
from data.client import cached_client
from execution.position_manager import manage_open_limit
from persistance.connection import Base, engine


class TradingBot:
    def __init__(self):
        self.client = cached_client()
        self.is_running = False
        self.db_path = "./general.db"

    def _setup_environment(self):
        """Initializes database and exchange settings."""
        if os.path.exists(self.db_path):
            logger.info("Database already exists.")
        else:
            logger.info("Initializing database...")
            Base.metadata.create_all(bind=engine)

        for symbol in settings.TradingConfig().list_of_interest:
            self.client.set_leverage(risk.RiskConfig().leverage, symbol)
            logger.debug(f"Leverage set for {symbol}")

    @logger.catch
    def start(self):
        """Main execution loop."""
        self._setup_environment()
        self.is_running = True
        logger.info("Bot started.")

        try:
            while self.is_running:
                manage_open_limit(self.client)
                e.avaliation_and_place(self.client)
                time.sleep(90)
        except KeyboardInterrupt:
            self.stop()

    def check_margin(self):
        bal = self.client.fetch_balance()
        print(bal["USDT"])

    def stop(self):
        """Graceful shutdown."""
        self.is_running = False
        logger.info("Loop stopped by user. Cleaning up...")

    def close_order(self, symbol: str, id: str):
        try:
            self.client.cancel_order(id, symbol)
        except Exception as err:
            logger.error(
                f"Due to {err}, it wasnt possible to close/cancel order: {id}, {symbol}"
            )

    def fet_order(self, symbol: str, id: Optional[str]):
        if id:
            try:
                self.client.fetch_open_order(id, symbol)
            except Exception as err:
                logger.error(
                    f"Due to {err}, it wasnt possible to fetch open order: {id}, {symbol}"
                )
        else:
            try:
                self.client.fetch_open_orders(symbol)
            except Exception as err:
                logger.error(
                    f"Due to {err}, it wasnt possible to fetch open orders of {symbol}"
                )
