import asyncio
import time
from typing import Optional

from loguru import logger
from numpy import asin

import data.fetch as fetch
from data.client import cached_client
from execution import risk_manager
from persistance.connection import SessionLocal
from persistance.models import GeneralOrder, TakeStopOrder

client = cached_client()
db = SessionLocal()


async def order(
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
        logger.error(f"Invalid side, actual side: {sell_buy}")
        return

    # 2. Place the Main Entry Order
    # Using entry_side ('buy' for bullish)
    entry_order = await client.create_order(market, t, entry_side, n, price)

    general_id = entry_order["id"]

    def save_entry():
        with db as session:
            try:
                new_order = GeneralOrder(
                    id=entry_order["id"],
                    price=entry_order["average"]
                    if t == "market"
                    else entry_order["price"],
                    entrance_exit="entrance",
                    amount=entry_order["amount"],
                    side=entry_order["side"],
                    symbol=entry_order["symbol"],
                    order_type=entry_order["type"],
                    time=entry_order["timestamp"],
                    previous_time=entry_order["lastTradeTimestamp"],
                )
                session.add(new_order)

                session.commit()

            except Exception as e:
                session.rollback()
                logger.error(f"An error occurred: {e}")

    await asyncio.to_thread(save_entry)

    # 3. Place Stop Loss
    tasks = []
    if stop_loss:
        tasks.append(order_ice(market, n, entry_side, None, stop_loss, general_id))
    if take_profit:
        tasks.append(order_ice(market, n, entry_side, take_profit, None, general_id))

    if tasks:
        await asyncio.gather(*tasks)


async def order_ice(
    market: str,
    total_amount: float,
    side: str,
    tp: Optional[float],
    sl: Optional[float],
    order_id: int,
):

    exit_side = "sell" if side == "buy" else "buy"

    # Logic for SL/TP placement
    target_price = sl if sl else tp
    order_type = "STOP_MARKET" if sl else "TAKE_PROFIT_MARKET"

    try:
        order_res = await client.create_order(
            symbol=market,
            type=order_type,
            side=exit_side,
            amount=total_amount,
            price=target_price,
            params={
                "stopPrice": target_price,
                "reduceOnly": True,
                "workingType": "MARK_PRICE",
            },
        )

        def save_tp_sl():
            with SessionLocal() as session:
                try:
                    g_order = session.get(GeneralOrder, order_id)
                    if sl:
                        g_order.stop_id = order_res["id"]
                    else:
                        g_order.take_id = order_res["id"]

                    new_order = TakeStopOrder(
                        id=order_res["id"],
                        parent_order_id=order_id,
                        price=order_res.get("triggerPrice", target_price),
                        amount=order_res["amount"],
                        side=order_res["side"],
                        symbol=order_res["symbol"],
                        order_type=order_type,
                        time=order_res["timestamp"],
                    )
                    session.add(new_order)
                    session.commit()
                except Exception as e:
                    session.rollback()
                    logger.error(f"DB Sync Error: {e}")

        await asyncio.to_thread(save_tp_sl)

    except Exception as e:
        logger.error(f"{order_type} Failed: {e}")


async def execute_iceberg(
    market: str, total_amount: float, side: str, tp: float, sl: float
):
    remaining_amount = total_amount
    chunk_size = total_amount * 0.1
    side = "buy" if side == "bullish" else "sell"

    while remaining_amount > 0:
        target_price = await risk_manager.blp(market, side, chunk_size)
        current_slice = min(chunk_size, remaining_amount)

        logger.info(f"Placing {side} limit order: {current_slice} at {target_price}")

        try:
            order = await client.create_order(
                market, "limit", side, current_slice, target_price, {"postOnly": True}
            )

            await order_ice(market, current_slice, side, tp, sl, order["id"])

            def ice_entry_db():
                with db as session:
                    try:
                        new_order = GeneralOrder(
                            id=order["id"],
                            price=order["average"],
                            entrance_exit="entrance",
                            amount=order["amount"],
                            side=order["side"],
                            symbol=order["symbol"],
                            order_type=order["type"],
                            time=order["timestamp"],
                            previous_time=order["lastTradeTimestamp"],
                        )
                        session.add(new_order)

                        session.commit()

                    except Exception as e:
                        session.rollback()
                        logger.error(f"An error occurred: {e}")

            await asyncio.to_thread(ice_entry_db)

        except Exception as e:
            logger.error(f"Order failed/rejected (possibly price changed): {e}")
            await asyncio.sleep(2)
            continue

        await asyncio.sleep(30)

        order_status = await fetch.get_order(order["id"], market)
        filled = order_status["filled"]
        remaining_amount -= filled

        if order_status["status"] != "closed":
            logger.info(
                f"Order partially filled. Canceling remaining {order_status['remaining']} to re-price."
            )

            def del_ice_entry():
                with db as session:
                    try:
                        entry = session.get(GeneralOrder, order["id"])
                        session.delete(entry)

                        session.commit()

                    except Exception as e:
                        session.rollback()
                        logger.error(f"DB Sync Error: {e}")

            await client.cancel_order(order["id"], market)

        logger.info(f"Remaining total to {side}: {remaining_amount}")

    logger.info(f"{market} Iceberg Execution Complete.")
