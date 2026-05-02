import time
from typing import Optional

from loguru import logger
from sqlalchemy.sql import False_

import data.fetch as fetch
from execution import risk_manager
from persistance.connection import SessionLocal
from persistance.models import GeneralOrder, TakeStopOrder

# --------------------- Helpers --------------------- #


def _order_ice(
    client,
    market: str,
    total_amount: float,
    side: str,
    tp: Optional[float],
    sl: Optional[float],
    order_id: str,
):
    """Sets Stop Loss and Take Profit for a specific iceberg slice."""
    exit_side = "sell" if side.lower() == "buy" else "buy"

    # Place Stop Loss
    if sl:
        _place_linked_order(
            client,
            market,
            "STOP_MARKET",
            exit_side,
            total_amount,
            sl,
            order_id,
            "stop_id",
            SessionLocal,
        )

    # Place Take Profit
    if tp:
        _place_linked_order(
            client,
            market,
            "TAKE_PROFIT_MARKET",
            exit_side,
            total_amount,
            tp,
            order_id,
            "take_id",
            SessionLocal,
        )


def _place_linked_order(
    client,
    market,
    order_type,
    side,
    amount,
    trigger_price,
    parent_id,
    id_field,
    session_factory,
):
    """
    Helper function to handle the repetitive logic of SL/TP
    to avoid UnboundLocalErrors and code duplication.
    """
    try:
        time.sleep(0.5)
        order_data = client.create_order(
            symbol=market,
            type=order_type,
            side=side,
            amount=amount,
            price=trigger_price,
            params={
                "stopPrice": trigger_price,
                "reduceOnly": True,
                "workingType": "MARK_PRICE",
            },
        )
        logger.info(f"Created {order_type}: {order_data['id']}")

        with session_factory() as session:
            try:
                parent = session.get(GeneralOrder, parent_id)
                if parent:
                    setattr(parent, id_field, order_data["id"])

                # Create Linked Order Record
                new_linked = TakeStopOrder(
                    id=order_data["id"],
                    parent_order_id=parent_id,
                    price=order_data.get("triggerPrice", trigger_price),
                    amount=order_data["amount"],
                    side=order_data["side"],
                    symbol=order_data["symbol"],
                    order_type=order_type,
                    time=order_data["timestamp"],
                )
                session.add(new_linked)
                session.commit()
            except Exception as e:
                session.rollback()
                logger.error(f"DB Error saving {order_type}: {e}")

    except Exception as e:
        logger.error(f"{order_type} API Failure: {e}")


# --------------------- Nominal Order --------------------- #


def order(
    client,
    market: str,
    type: str,
    sell_buy: str,
    amount: float,
    price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    take_profit: Optional[float] = None,
):
    # 1. Determine Sides
    entry_side = sell_buy.lower()
    exit_side = "sell" if entry_side == "buy" else "buy"

    # 2. Place Main Entry Order
    try:
        entry_order = client.create_order(
            market,
            type,
            entry_side,
            amount,
            price,
            {"postOnly": True} if type == "limit" else False,
        )
        general_id = entry_order["id"]
        logger.info(f"Created entry: {general_id}")
    except Exception as e:
        logger.error(f"Entry Order Failed: {e}")
        return None

    # 3. Persist Entry Order
    with SessionLocal() as session:
        try:
            new_order = GeneralOrder(
                id=general_id,
                price=entry_order.get("average")
                if type == "market"
                else entry_order.get("price"),
                entrance_exit="entrance",
                amount=entry_order["amount"],
                side=entry_order["side"],
                symbol=entry_order["symbol"],
                order_type=entry_order["type"],
                time=entry_order["timestamp"],
            )
            session.add(new_order)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error saving Entry: {e}")

    # 4. Place Stop Loss
    if stop_loss:
        _place_linked_order(
            client,
            market,
            "STOP_MARKET",
            exit_side,
            amount,
            stop_loss,
            general_id,
            "stop_id",
            session_factory=SessionLocal,
        )

    # 5. Place Take Profit
    if take_profit:
        _place_linked_order(
            client,
            market,
            "TAKE_PROFIT_MARKET",
            exit_side,
            amount,
            take_profit,
            general_id,
            "take_id",
            session_factory=SessionLocal,
        )


# --------------------- Ice --------------------- #


def execute_iceberg(
    client, market: str, total_amount: float, side: str, tp: float, sl: float
):
    remaining_amount = total_amount
    chunk_size = total_amount * 0.1

    # Normalize side
    normalized_side = side

    if normalized_side not in ["buy", "sell"]:
        logger.error(f"Invalid side provided: {side}")
        return

    while remaining_amount > 0:
        # 1. Get current market depth/target price
        target_price = risk_manager.blp(market, normalized_side, chunk_size)
        current_slice = min(chunk_size, remaining_amount)

        logger.info(
            f"Iceberg Slice: {normalized_side} {current_slice} at {target_price}"
        )

        try:
            # 2. Create the Entry Order
            order_resp = client.create_order(
                market,
                "limit",
                normalized_side,
                current_slice,
                target_price,
                {"postOnly": True},
            )
            order_id = order_resp["id"]

            # 3. Save Entry to DB immediately
            with SessionLocal() as session:
                try:
                    new_order = GeneralOrder(
                        id=order_id,
                        price=order_resp.get("average", target_price),
                        entrance_exit="entrance",
                        amount=order_resp["amount"],
                        side=order_resp["side"],
                        symbol=order_resp["symbol"],
                        order_type=order_resp["type"],
                        time=order_resp["timestamp"],
                    )
                    session.add(new_order)
                    session.commit()
                except Exception as db_e:
                    session.rollback()
                    logger.error(f"Iceberg DB Error: {db_e}")

            # 4. Attach Protection (SL/TP)
            _order_ice(client, market, current_slice, normalized_side, tp, sl, order_id)

            # 5. Wait for fill (Iceberg logic)
            time.sleep(30)

            # 6. Check Status & Re-evaluate
            order_status = fetch.get_order(order_id, market)
            filled = order_status.get("filled", 0)
            remaining_amount -= filled

            if order_status["status"] != "closed":
                logger.info(f"Slice partially filled ({filled}). Canceling remainder.")
                try:
                    client.cancel_order(order_id, market)
                except Exception as e:
                    logger.warning(f"Could not cancel order {order_id}: {e}")

            logger.info(f"Total remaining for iceberg: {remaining_amount}")

        except Exception as e:
            logger.error(f"Slice failed: {e}")
            time.sleep(2)
            continue

    logger.info(
        f"Finished Iceberg for {market}. Total filled: {total_amount - remaining_amount}"
    )
