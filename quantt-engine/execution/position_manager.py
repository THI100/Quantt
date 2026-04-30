from loguru import logger
from sqlalchemy import desc, select

import data.fetch as fetch
from config import settings
from execution import risk_manager as rm
from persistance.connection import SessionLocal
from persistance.models import (
    GeneralOrder,
    TakeStopOrder,
)


def manage_open_symbols():
    symbol_status = {}

    # Using context manager for the entire loop to ensure session safety
    with SessionLocal() as session:
        try:
            for symbol in settings.watcher.get_config().list_of_interest:
                stmt = (
                    select(GeneralOrder)
                    .filter(GeneralOrder.symbol.like(f"{symbol}%"))
                    .order_by(desc(GeneralOrder.time))
                )
                last_record = session.execute(stmt).scalars().first()

                if not last_record or last_record.entrance_exit == "exit":
                    symbol_status[symbol] = "open"
                    continue

                exchange_trades = fetch.get_orders(symbol, limit=5)
                is_now_closed_on_exchange = False

                for trade in exchange_trades:
                    trade_id = str(trade["id"])
                    is_opposite_side = trade["side"].lower() != last_record.side.lower()
                    is_reduce_only = (
                        str(trade.get("info", {}).get("reduceOnly")).lower() == "true"
                    )
                    is_after_entrance = str(trade["timestamp"]) > str(last_record.time)

                    if is_opposite_side and (is_reduce_only and is_after_entrance):
                        # Check if this SPECIFIC trade is already our exit record
                        already_exists = session.get(GeneralOrder, trade_id)
                        if already_exists:
                            is_now_closed_on_exchange = True
                            break

                        tp_price = (
                            last_record.take_order.price
                            if last_record.take_order
                            else None
                        )
                        is_tp_hit = (
                            tp_price
                            and abs(trade["price"] - tp_price) / tp_price < 0.0005
                        )

                        exit_order = GeneralOrder(
                            id=trade_id,
                            entrance_exit="exit",
                            price=trade["price"],
                            amount=trade["amount"],
                            side=trade["side"].lower(),
                            symbol=last_record.symbol,
                            order_type="limit" if is_tp_hit else "market",
                            time=str(trade["timestamp"]),
                            previous_time=str(last_record.time),
                        )

                        session.add(exit_order)
                        is_now_closed_on_exchange = True
                        break

                if is_now_closed_on_exchange:
                    session.commit()
                    symbol_status[symbol] = "open"
                else:
                    symbol_status[symbol] = "closed"

        except Exception as e:
            session.rollback()
            logger.error(
                f"Error syncing {symbol if 'symbol' in locals() else 'unknown'}: {e}"
            )

    return symbol_status


def manage_open_limit(client):
    typ = "limit"

    for symbol in settings.watcher.get_config().list_of_interest:
        current_open = fetch.get_open_orders(symbol, 10)

        for x in current_open:
            if x.get("reduceOnly") is True or x.get("status") == "filled":
                continue

            order_id = str(x.get("id"))

            with SessionLocal() as session:
                old_order = session.get(GeneralOrder, order_id)
                if not old_order:
                    continue

                s = x.get("side").lower()
                amt = x.get("amount")
                p = rm.blp(symbol, s, amt)

                try:
                    # 1. Exchange Action
                    client.cancel_order(order_id, symbol)
                    new_exchange_order = client.create_order(symbol, typ, s, amt, p)
                    new_id = str(new_exchange_order["id"])

                    # 2. Create NEW parent first
                    new_order_record = GeneralOrder(
                        id=new_id,
                        price=new_exchange_order.get("price"),
                        entrance_exit="entrance",
                        amount=new_exchange_order.get("amount", amt),
                        side=new_exchange_order.get("side"),
                        symbol=symbol,
                        order_type=typ,
                        time=str(new_exchange_order.get("timestamp")),
                        previous_time=str(new_exchange_order.get("lastTradeTimestamp")),
                    )
                    session.add(new_order_record)
                    session.flush()  # Makes new_id available for FKs

                    # 3. Re-link children to the NEW ID
                    children = (
                        session.query(TakeStopOrder)
                        .filter_by(parent_order_id=order_id)
                        .all()
                    )
                    for child in children:
                        child.parent_order_id = new_id

                    # 4. Delete old parent and commit
                    session.delete(old_order)
                    session.commit()
                    logger.info(f"Successfully migrated {order_id} to {new_id}")

                except Exception as e:
                    session.rollback()
                    logger.error(f"Failed to manage order {order_id}: {e}")
