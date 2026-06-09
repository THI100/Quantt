import sys
from pathlib import Path

from loguru import logger

from config import settings

if getattr(sys, "frozen", False):
    DIR = Path(sys.executable).parent
else:
    DIR = Path(__file__).resolve().parent.parent

ENV_PATH = DIR / "qdata" / ".env"
ENV_PATH.parent.mkdir(parents=True, exist_ok=True)

if not ENV_PATH.exists():
    ENV_PATH.touch()

if ENV_PATH.stat().st_size == 0:
    logger.error(
        "Oops, it seems you dont have data on your .env, write directly on it or use the API page to modify the values."
    )


def get_exchange_client(exchange_name: str = settings.watcher.get_config().exchange):
    if exchange_name == "bybit":
        from exchange.bybit import bb_client

        return bb_client

    elif exchange_name == "binance":
        from exchange.binance import bi_client

        return bi_client

    elif exchange_name == "okx":
        from exchange.okx import okx_client

        return okx_client

    elif exchange_name == "mexc":
        from exchange.mexc import mx_client

        return mx_client

    else:
        logger.error(f"Unsupported exchange: {exchange_name}")
