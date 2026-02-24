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


def blp(market: str, side: str, amount: float):
    """
    Search for the best price for limit type of orders, utilizing the order book.
    there might be some delays and inacuracies compared to the order book.
    """

    order_book = fetch.get_order_book(market)
    ticker = fetch.get_ticker(market)
    lp = ticker["last"]

    levels = order_book["bids"] if side == "buy" else order_book["asks"]

    target_liquidity = amount * 3
    cumulative_volume = 0
    chosen_price = None

    if amount <= 0:
        return ValueError("Invalid amount")
    else:
        for price, vol in levels:
            cumulative_volume += vol
            if cumulative_volume >= target_liquidity:
                chosen_price = price
                break

            # Fallback if the book is thin
            if not chosen_price:
                chosen_price = levels[0][0]
                # Safety Check: Compare with Last Price to avoid 'Price Peaks'
            price_deviation = abs(chosen_price - lp) / lp

            if price_deviation > 0.005:
                # Move price 0.1% offset from Last Price instead of deep book level
                offset = 0.001 if side == "buy" else -0.001
                chosen_price = last_price * (1 - offset)

    return chosen_price
