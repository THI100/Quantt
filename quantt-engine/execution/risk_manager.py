from decimal import ROUND_HALF_UP, Decimal

import config.risk as risk
import data.cache as cache
import data.fetch as fetch
import numpy as np


def smart_amount(market: str):
    bal = fetch.balance()
    ticker = fetch.get_ticker(market)
    last = ticker["last"]
    usdt_n = bal["USDT"]["free"]

    limited = usdt_n * risk.porcentage_of_capital_per_trade

    ma = limited / last

    market_amount = ma.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    return market_amount
