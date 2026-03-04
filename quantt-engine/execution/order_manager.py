import time
from typing import Optional

import data.fetch as fetch
from data.client import cached_client
from execution import risk_manager
from persistance.connection import SessionLocal
from persistance.models import GeneralOrder, TakeStopOrder

client = cached_client()
db = SessionLocal()


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

    general_id = entry_order["id"]

    with db as session:
        try:
            new_order = GeneralOrder(
                id=entry_order["id"],
                price=entry_order["average"],
                entrace_exit="entrace",
                amount=entry_order["amount"],
                side=entry_order["side"],
                symbol=entry_order["symbol"],
                order_type=entry_order["type"],
                time=entry_order["timestamp"],
                previous_time=entry_order["lastTradeTimestamp"],
            )
            session.add(new_order)

            session.commit()
            print(f"Entry Filled: {entry_order['id']} and saved!!!")

        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")

    # 3. Place Stop Loss
    if stop_loss:
        type = "STOP_MARKET"
        try:
            sl_order = client.create_order(
                symbol=market,
                type=type,
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

        with db as session:
            try:
                g_order = session.get(GeneralOrder, general_id)
                g_order.stop_id = sl_order["id"]
                new_order = TakeStopOrder(
                    id=sl_order["id"],
                    parent_order_id=general_id,
                    price=sl_order["triggerPrice"],
                    amount=sl_order["amount"],
                    side=sl_order["side"],
                    symbol=sl_order["symbol"],
                    order_type=type,
                    time=sl_order["timestamp"],
                )
                session.add(new_order)

                session.commit()
                print(f"Entry Filled: {sl_order['id']} and saved!!!")

            except Exception as e:
                session.rollback()
                print(f"An error occurred: {e}")

    # 4. Place Take Profit
    if take_profit:
        type = "TAKE_PROFIT_MARKET"
        try:
            tp_order = client.create_order(
                symbol=market,
                type=type,
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

        with db as session:
            try:
                g_order = session.get(GeneralOrder, general_id)
                g_order.take_id = tp_order["id"]
                new_order = TakeStopOrder(
                    id=tp_order["id"],
                    parent_order_id=general_id,
                    price=tp_order["triggerPrice"],
                    amount=tp_order["amount"],
                    side=tp_order["side"],
                    symbol=tp_order["symbol"],
                    order_type=type,
                    time=tp_order["timestamp"],
                )
                session.add(new_order)
                session.commit()
                print(f"Entry Filled: {tp_order['id']} and saved!!!")

            except Exception as e:
                session.rollback()
                print(f"An error occurred: {e}")

    return entry_order, tp_order, sl_order


def execute_iceberg(market: str, total_amount: float, side: str):
    remaining_amount = total_amount
    # Break the order into 10% chunks to hide our size
    chunk_size = total_amount * 0.1

    while remaining_amount > 0:
        price_data = risk_manager.blp(market, side, chunk_size)
        target_price = price_data

        current_slice = min(chunk_size, remaining_amount)

        print(f"Placing {side} limit order: {current_slice} at {target_price}")

        try:
            order = client.create_order(
                market, "limit", side, current_slice, target_price, {"postOnly": True}
            )
        except Exception as e:
            print(f"Order failed/rejected (possibly price changed): {e}")
            time.sleep(2)
            continue

        time.sleep(30)

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
