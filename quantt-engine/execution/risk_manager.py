from typing import Optional

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

    market_amount = round(ma, 4)

    return market_amount


def blp(market: str, amount: Optional[float] = 0):
    """
    Search for the best price for limit type of orders, utilizing the order book.
    there might be some delays and inacuracies compared to the order book.
    """

    order_book = fetch.get_order_book(market)
    lp = fetch.get_ticker(market)
    lp = lp["last"]

    if amount <= 0:
        # return error
    elif amount > 1.0:
        # apply iceberg
    else:
        # apply at best

    return
