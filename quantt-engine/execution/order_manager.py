import time
from typing import Optional

import data.fetch as fetch
from data.client import cached_client
from execution import risk_manager

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
            sl_order = client.create_order(
                symbol=market,
                type="STOP_MARKET",
                side=exit_side,  # Must be 'sell' if entry was 'buy'
                amount=n,
                price=stop_loss,  # The price it executes at
                params={
                    "stopPrice": stop_loss,
                    "reduceOnly": True,
                    "workingType": "MARK_PRICE",
                },
            )
        except Exception as e:
            print(f"Stop Loss Failed: {e}")

    # 4. Place Take Profit
    if take_profit:
        try:
            tp_order = client.create_order(
                symbol=market,
                type="TAKE_PROFIT_MARKET",
                side=exit_side,
                amount=n,
                price=take_profit,
                params={
                    "stopPrice": take_profit,
                    "reduceOnly": True,
                    "workingType": "MARK_PRICE",
                },
            )
        except Exception as e:
            print(f"Take Profit Failed: {e}")

    return entry_order, tp_order, sl_order


def execute_iceberg(market: str, total_amount: float, side: str):
    remaining_amount = total_amount
    # Break the order into 10% chunks to hide our size
    chunk_size = total_amount * 0.1

    while remaining_amount > 0:
        # 1. Find the "Meaningful" Price Level using our blp logic
        # We pass chunk_size to ensure we find a level that can handle this slice
        price_data = risk_manager.blp(market, side, chunk_size)
        target_price = price_data

        current_slice = min(chunk_size, remaining_amount)

        print(f"Placing {side} limit order: {current_slice} at {target_price}")

        # 2. Place a Post-Only order to ensure Maker fees
        # (Assuming 'exchange' is your initialized CCXT object)
        try:
            order = client.create_order(
                market, "limit", side, current_slice, target_price, {"postOnly": True}
            )
        except Exception as e:
            print(f"Order failed/rejected (possibly price changed): {e}")
            time.sleep(2)  # cooling off
            continue

        # 3. Wait/Monitor Period (e.g., 30 seconds)
        # Give the market time to come to our limit price
        time.sleep(30)

        # 4. Check status and Cancel if not fully filled
        order_status = fetch.get_order(order["id"], market)
        filled = order_status["filled"]
        remaining_amount -= filled

        if order_status["status"] != "closed":
            print(
                f"Order partially filled. Canceling remaining {order_status['remaining']} to re-price."
            )
            client.cancel_order(order["id"], market)

        print(f"Remaining total to buy/sell: {remaining_amount}")

    print("Execution Complete.")
