from loguru import logger
from sqlalchemy import desc, select

import config.settings as settings
import data.fetch as fetch
from execution import risk_manager as rm
from persistance.connection import SessionLocal
from persistance.models import (
    GeneralOrder,
    TakeStopOrder,
)


def manage_open_symbols():
    symbol_status = {}
    session = SessionLocal()

    try:
        for symbol in settings.list_of_interest:
            # 1. Fetch the absolute latest record for this symbol
            stmt = (
                select(GeneralOrder)
                .filter(GeneralOrder.symbol.like(f"{symbol}%"))
                .order_by(desc(GeneralOrder.time))
            )
            last_record = session.execute(stmt).scalars().first()

            # If no history exists, or the last action was an EXIT, the market is OPEN
            if not last_record or last_record.entrance_exit == "exit":
                symbol_status[symbol] = "open"
                continue

            # 2. If the last record was an "entrace", we check if the Exchange closed it
            exchange_trades = fetch.get_orders(
                symbol, limit=2
            )  # Increased limit for safety
            is_now_closed_on_exchange = False

            for trade in exchange_trades:
                # 1. Basic Verification
                is_opposite_side = trade["side"].lower() != last_record.side.lower()
                is_reduce_only = trade.get("info", {}).get("reduceOnly") in [
                    True,
                    "true",
                    "True",
                ]

                # 2. Timing Verification (Must be after the entrance)
                is_after_entrance = trade["timestamp"] > last_record.time

                if is_opposite_side and (is_reduce_only and is_after_entrance):
                    # 3. Check if already logged
                    already_exists = (
                        session.execute(
                            select(GeneralOrder).filter(
                                GeneralOrder.id == str(trade["id"])
                            )
                        )
                        .scalars()
                        .first()
                    )

                    if already_exists:
                        is_now_closed_on_exchange = True
                        break

                    # 4. Determine why it closed (for your records)
                    tp_price = (
                        last_record.take_order.price if last_record.take_order else None
                    )

                    # We consider it a "Limit/TP" only if it's very close to the TP price
                    # Otherwise, we treat it as a Market exit (Manual, SL, or Break-Even)
                    is_tp_hit = (
                        tp_price and abs(trade["price"] - tp_price) / tp_price < 0.0005
                    )

                    exit_order = GeneralOrder(
                        id=str(trade["id"]),
                        entrance_exit="exit",
                        price=trade["price"],
                        amount=trade["amount"],
                        side=trade["side"].lower(),
                        symbol=last_record.symbol,
                        order_type="limit"
                        if is_tp_hit
                        else "market",  # BE/SL usually execute as market
                        time=trade["timestamp"],
                        previous_time=last_record.time,
                    )

                    session.add(exit_order)
                    is_now_closed_on_exchange = True
                    break

            if is_now_closed_on_exchange:
                session.commit()
                symbol_status[symbol] = "open"  # Trade finished, symbol now available
            else:
                symbol_status[symbol] = "closed"  # Trade still active, symbol occupied

    except Exception as e:
        session.rollback()
        logger.error(f"Error syncing {symbol}: {e}")
    finally:
        session.close()

    return symbol_status


def manage_open_limit(client):
    typ = "limit"

    for symbol in settings.list_of_interest:
        current_open = fetch.get_open_orders(symbol, 10)

        for x in current_open:
            # 1. Skip logic (Exchange status)
            if x.get("reduceOnly") is True or x.get("status") == "filled":
                continue

            order_id = x.get("id")

            # --- DATABASE CHECK START ---
            with SessionLocal() as session:
                # Check if this order ID exists in our DB
                db_order = session.get(GeneralOrder, order_id)

                if not db_order:
                    logger.info(f"Order {order_id} not found in DB. Skipping.")
                    continue
            # --- DATABASE CHECK END ---

            s = x.get("side").lower()
            amt = x.get("amount")

            # 2. Risk Management calculation
            p = rm.blp(symbol, s, amt)

            # 4. Execute Exchange & DB changes
            with SessionLocal() as session:
                try:
                    # 1. Cancel existing on exchange
                    client.cancel_order(order_id, symbol)
                    old_order = session.get(GeneralOrder, order_id)

                    # 2. Create new order on exchange
                    new_exchange_order = client.create_order(symbol, typ, s, amt, p)

                    # FORCED TYPE CAST: Ensure ID is an integer if your DB expects it
                    new_id = int(new_exchange_order["id"])

                    # 3. Create and add the NEW parent record FIRST
                    new_order_record = GeneralOrder(
                        id=new_id,
                        price=new_exchange_order.get("price"),
                        entrance_exit="entrance",
                        amount=new_exchange_order.get("amount", amt),
                        side=new_exchange_order.get("side"),
                        symbol=symbol,
                        order_type=typ,
                        time=new_exchange_order.get("timestamp"),
                        previous_time=new_exchange_order.get("lastTradeTimestamp"),
                    )
                    session.add(new_order_record)

                    # IMPORTANT: Flush tells the DB about the new_id without closing the transaction
                    session.flush()

                    # 4. Now update the children (the Foreign Key will now find the parent)
                    children = (
                        session.query(TakeStopOrder)
                        .filter(TakeStopOrder.parent_order_id == order_id)
                        .all()
                    )
                    for child in children:
                        child.parent_order_id = new_id

                    # 5. Clean up the old record and commit everything
                    if old_order:
                        session.delete(old_order)

                    session.commit()
                    logger.info(f"Successfully migrated {order_id} to {new_id}")

                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to manage order {order_id}: {e}")
