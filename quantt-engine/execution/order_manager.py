from typing import Optional

from data.client import cached_client

client = cached_client()


def order(
    market: str,
    t: str,
    sell_buy: str,
    n: float,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
):
    # 1. Determine Entry and Exit Sides
    if sell_buy == "bullish":
        entry_side = "buy"
        exit_side = "sell"
    elif sell_buy == "bearish":
        entry_side = "sell"
        exit_side = "buy"
    else:
        raise ValueError("Invalid side")

    # 2. Place the Main Entry Order
    # Using entry_side ('buy' for bullish)
    entry_order = client.create_order(market, t, entry_side, n, price)
    print(f"Entry Filled: {entry_order['id']}")

    # 3. Place Stop Loss
    if stop_loss:
        try:
            client.create_order(
                symbol=market,
                type="STOP_MARKET",  # Most reliable for Spot
                side=exit_side,  # Must be 'sell' if entry was 'buy'
                amount=n,
                price=stop_loss,  # The price it executes at
                params={"stopPrice": stop_loss, "reduceOnly": True},
            )
        except Exception as e:
            print(f"Stop Loss Failed: {e}")

    # 4. Place Take Profit
    if take_profit:
        try:
            client.create_order(
                symbol=market,
                type="TAKE_PROFIT_MARKET",
                side=exit_side,
                amount=n,
                price=take_profit,
                params={"stopPrice": take_profit, "reduceOnly": True},
            )
        except Exception as e:
            print(f"Take Profit Failed: {e}")

    # # 3. Place Stop Loss (Using exit_side!)
    # if stop_loss:
    #     try:
    #         client.create_order(
    #             symbol=market,
    #             type="STOP_LOSS_LIMIT",  # Most reliable for Spot
    #             side=exit_side,  # Must be 'sell' if entry was 'buy'
    #             amount=n,
    #             price=stop_loss,  # The price it executes at
    #             params={
    #                 "stopPrice": stop_loss,  # The price that triggers it
    #             },
    #         )
    #     except Exception as e:
    #         print(f"Stop Loss Failed: {e}")

    # # 4. Place Take Profit (Using exit_side!)
    # if take_profit:
    #     try:
    #         client.create_order(
    #             symbol=market,
    #             type="TAKE_PROFIT_LIMIT",
    #             side=exit_side,  # Must be 'sell' if entry was 'buy'
    #             amount=n,
    #             price=take_profit,
    #             params={
    #                 "stopPrice": take_profit,
    #             },
    #         )
    #     except Exception as e:
    #         print(f"Take Profit Failed: {e}")

    return "Success"
