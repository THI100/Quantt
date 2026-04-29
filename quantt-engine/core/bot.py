import os
import threading
import time
from typing import Optional

from loguru import logger

import core.engine as e
from config import risk, settings
from data.client import cached_client
from execution.position_manager import manage_open_limit
from persistance.connection import Base, engine
from utils.math import scale_0_100


class TradingBot:
    def __init__(self):
        self.client = cached_client()
        self.is_running = False
        self.db_path = "./general.db"
        self.stop_event = threading.Event()

    def setup_environment(self):
        """Initializes database and exchange settings."""
        if os.path.exists(self.db_path):
            logger.info("Database already exists.")
        else:
            logger.info("Initializing database...")
            Base.metadata.create_all(bind=engine)

        self.client.load_markets()

        for symbol in settings.watcher.get_config().list_of_interest:
            try:
                self.client.set_leverage(risk.watcher.get_config().leverage, symbol)
                logger.debug(f"Leverage set for {symbol}")
            except Exception as err:
                logger.error(f"Error occured, when setting Leverage: {err}")

    @logger.catch
    def start(self, paused_check_func=None):
        """Main execution loop."""
        # self.setup_environment()
        self.is_running = True
        self.stop_event.clear()
        logger.info("Bot started.")

        try:
            while self.is_running:
                if paused_check_func and paused_check_func():
                    time.sleep(5)  # Low CPU usage while paused
                    continue

                manage_open_limit(self.client)
                e.avaliation_and_place(self.client)

                if self.stop_event.wait(timeout=90):
                    break

        except KeyboardInterrupt:
            self.stop()
        finally:
            self.is_running = False

    def check_bal(self):
        bal = self.client.fetch_balance()
        ut = bal["USDT"]
        uc = bal["USDC"]
        ut.update({"coin": "USDT"})
        uc.update({"coin": "USDC"})
        return ut, uc

    def check_margin(self):
        b = self.check_bal()
        dic = {}
        for c in b:
            margin_health = scale_0_100(c["used"], c["total"])
            dic.update({c["coin"]: margin_health})
        return dic

    def stop(self):
        """Graceful shutdown."""
        self.is_running = False
        self.stop_event.set()
        logger.info("Loop stopped by user. Cleaning up...")

    def close_order(self, symbol: str, id: str):
        try:
            self.client.cancel_order(id, symbol)
        except Exception as err:
            logger.error(
                f"Due to {err}, it wasnt possible to close/cancel order: {id}, {symbol}"
            )

    def fet_order(self, symbol: str, id: Optional[str] = None):
        if id:
            try:
                print("hi2")
                return self.client.fetch_order(id, symbol)
            except Exception as err:
                logger.error(
                    f"Due to {err}, it wasnt possible to fetch open order: {id}, {symbol}"
                )
                return []
        else:
            try:
                print("hi")
                return self.client.fetch_orders(symbol)
            except Exception as err:
                logger.error(
                    f"Due to {err}, it wasnt possible to fetch open orders of {symbol}"
                )
                return []
