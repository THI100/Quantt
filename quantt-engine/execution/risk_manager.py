import math

from loguru import logger

import data.fetch as fetch
from config import risk

r = risk.watcher.get_config()


def smart_amount(market: str):
    try:
        # 1. Fetch data
        bal = fetch.balance()
        ticker = fetch.get_ticker(market)

        last = ticker.get("last") or ticker.get("close")

        # 3. Extract Balance
        usdt_n = bal.get("USDT", {}).get("free")

        # 4. Safety Check: Avoid Division by Zero
        if not last or last <= 0 or math.isnan(last):
            return 0.0

        # 5. Calculation Logic
        percentage = getattr(r, "percentage_of_capital_per_trade", 0.0)
        leverage = getattr(r, "leverage", 1.0)

        limited = usdt_n * percentage
        ma = (limited / last) * leverage

        # 6. Final Polish
        # Check result one last time before rounding
        if math.isnan(ma) or math.isinf(ma):
            return 0.0

        return round(ma, 4)

    except Exception as e:
        # Log the error if necessary: logger.info(f"Error in smart_amount: {e}")
        return 0.0


def blp(market: str, side: str, amount: float):
    """
    Search for the best price for limit type of orders, utilizing the order book.
    there might be some delays and inacuracies compared to the order book.
    """

    order_book = fetch.get_order_book(market)
    ticker = fetch.get_ticker(market)
    lp = ticker["last"]

    if side == "bullish" or side == "buy" or side == "Buy":
        side = "buy"
    elif side == "bearish" or side == "sell" or side == "sell":
        side = "sell"
    else:
        logger.error(f"Invalid side, actual side: {side}")

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
                chosen_price = lp * (1 - offset)

    return chosen_price
