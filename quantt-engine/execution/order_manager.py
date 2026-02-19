from typing import Literal, Optional

from data.client import cached_client

# Define the allowed types for the linter
# OrderType = Literal['market', 'limit', 'stop', 'take_profit']
# OrderSide = Literal['bullish', 'bearish']
client = cached_client()


def order(
    market: str,
    t: str,
    sell_buy: str,
    n: float,
    price: Optional[float] = None,  # Fixed Error #1
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
):
    # Standardize side
    side: Literal["buy", "sell"]
    if sell_buy == "bearish":
        side = "sell"
    elif sell_buy == "bullish":
        side = "buy"
    else:
        raise ValueError("Invalid side")

    # Build params for Binance/CCXT
    params = {}
    if stop_loss:
        params["stopLossPrice"] = stop_loss  # Binance specific key
    if take_profit:
        params["takeProfitPrice"] = take_profit

    # By passing 'price' even if it is None, CCXT handles
    # it correctly based on the 't' (type) parameter.
    return client.create_order(
        symbol=market, type=t, side=side, amount=n, price=price, params=params
    )


def check_orders():

    return
