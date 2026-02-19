from asyncio.windows_events import NULL

from data.client import cached_client

client = cached_client()


def order(
    market: str,
    t: str,  # 'market' or 'limit'
    sell_buy: str,  # "bearish" or "bullish"
    n: float,
    price: float = None,
    stop_loss: float = None,
    take_profit: float = None,
):
    # 1. Standardize the Side
    if sell_buy == "bearish":
        side = "sell"
    elif sell_buy == "bullish":
        side = "buy"
    else:
        raise ValueError(f"Invalid side: {sell_buy}. Use 'bearish' or 'bullish'.")

    # 2. Build the params dictionary for CCXT
    # Binance uses 'stopPrice' for stop orders, but for bracket orders
    # (entry + SL/TP), CCXT uses a unified 'params' structure.
    params = {}

    if stop_loss:
        params["stopLossPrice"] = stop_loss
    if take_profit:
        params["takeProfitPrice"] = take_profit

    # 3. Create the order
    # Note: price is required for 'limit' orders, can be None for 'market'
    return client.create_order(
        symbol=market, type=t, side=side, amount=n, price=price, params=params
    )


def check_orders():

    return NULL
