import logging

from sqlalchemy import desc, select

import config.settings as settings
import data.fetch as fetch
from execution import risk_manager as rm
from persistance.connection import SessionLocal
from persistance.models import (
    GeneralOrder,
    TakeStopOrder,
)

logger = logging.getLogger(__name__)


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

            if last_record:
                print(f"DEBUG: {symbol} last state: '{last_record.entrance_exit}'")
            else:
                print(f"DEBUG: {symbol} has NO records in DB.")

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
                    print(
                        f"DEBUG: Detected Exit for {symbol} at {trade['price']} (Side: {trade['side']})"
                    )
                    break

            if is_now_closed_on_exchange:
                session.commit()
                symbol_status[symbol] = "open"  # Trade finished, symbol now available
            else:
                symbol_status[symbol] = "closed"  # Trade still active, symbol occupied

    except Exception as e:
        session.rollback()
        print(f"Error syncing {symbol}: {e}")
    finally:
        session.close()

    return symbol_status


def manage_open_limit(client):
    typ = "limit"

    for symbol in settings.list_of_interest:
        current_open = fetch.get_open_orders(symbol, 10)

        for x in current_open:
            # 1. Skip logic
            if x.get("reduceOnly") is True or x.get("status") == "filled":
                continue

            s = x.get("side").lower()
            amt = x.get("amount")
            order_id = x.get("id")

            # 2. Risk Management calculation
            p = rm.blp(symbol, s, amt)

            # 4. Execute Exchange & DB changes
            with SessionLocal() as session:
                try:
                    # Cancel existing
                    client.cancel_order(order_id, symbol)

                    # Delete old record from DB
                    old_order = session.get(GeneralOrder, order_id)

                    # Create new order on exchange
                    new_exchange_order = client.create_order(symbol, typ, s, amt, p)
                    new_id = new_exchange_order["id"]

                    children = (
                        session.query(TakeStopOrder)
                        .filter(TakeStopOrder.parent_order_id == order_id)
                        .all()
                    )
                    for child in children:
                        child.parent_order_id = new_id

                    # Save new order to DB
                    new_order_record = GeneralOrder(
                        id=new_exchange_order["id"],
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

                    if old_order:
                        session.delete(old_order)

                        session.commit()
                        print(f"Successfully migrated children to new order {new_id}")

                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to manage order {order_id}: {e}")
