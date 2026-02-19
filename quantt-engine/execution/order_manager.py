from asyncio.windows_events import NULL

from data.client import cached_client as client


def order(
    market: str, t: str, sell_buy: str, n: float, stop_loss: float, take_profit: float
):
    """
    market: symbol of your choice (example: "BTC/USDT")
    t: type of your order (Types: 'market' or 'limit' or 'STOP_LOSS' or 'STOP_LOSS_LIMIT' or 'TAKE_PROFIT' or 'TAKE_PROFIT_LIMIT' or 'STOP'), usually you will USE 'market'
    sell_buy: "bearish" or "bullish"
    n: amount of funds on this trade, recommended using risk_manager smart_amount
    stop_loss: given by get_loss_and_profit_stops function
    take_profit: given by get_loss_and_profit_stops function
    """

    p = [stop_loss, take_profit]

    if sell_buy == "bearish":
        sell_buy = "sell"
    else:
        sell_buy = "buy"

    return client.create_order(symbol=market, type=t, side=sell_buy, amount=n, params=p)


def check_orders():

    return NULL
