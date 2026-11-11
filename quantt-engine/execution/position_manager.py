from loguru import logger
from sqlalchemy import desc, select

from config import trading
from data import fetch
from execution import risk_manager as rm
from persistance.connection import SessionLocal
from persistance.models import (
    GeneralOrder,
    TakeStopOrder,
)
from utils.rate_lim import std_call

active_exchange = trading.watcher.get_config().exchange


def manage_open_symbols():
    symbol_status = {}

    # Using context manager for the entire loop to ensure session safety
    with SessionLocal() as session:
        try:
            for symbol in trading.watcher.get_config().list_of_interest:
                stmt = (
                    select(GeneralOrder)
                    .filter(GeneralOrder.symbol.like(f"{symbol}%"))
                    .filter(GeneralOrder.exchange == active_exchange)
                    .order_by(desc(GeneralOrder.time))
                )
                last_record = session.execute(stmt).scalars().first()

                if not last_record or last_record.entrance_exit == "exit":
                    symbol_status[symbol] = "open"
                    continue

                try:
                    exchange_trades = fetch.get_orders(symbol)
                except Exception as err:
                    logger.warning(
                        f"Due to the following error: {err}, it is needed to make the usage of a slower method."
                    )
                    exchange_trades = fetch.get_generalized(symbol)

                is_now_closed_on_exchange = False

                for trade in exchange_trades:
                    api_trade_id = trade.get("id")
                    if api_trade_id is None:
                        continue
                    trade_id = str(api_trade_id)
                    is_opposite_side = trade["side"].lower() != last_record.side.lower()
                    is_reduce_only = (
                        str(trade.get("info", {}).get("reduceOnly")).lower() == "true"
                    )
                    is_after_entrance = str(trade["timestamp"]) > str(last_record.time)

                    if is_opposite_side and (is_reduce_only and is_after_entrance):
                        # Check if this SPECIFIC trade is already our exit record
                        already_exists = session.execute(
                            select(GeneralOrder.id).where(
                                GeneralOrder.id == trade_id,
                                GeneralOrder.exchange == active_exchange,
                            )
                        ).scalar_one_or_none()
                        if already_exists:
                            is_now_closed_on_exchange = True
                            break

                        take_order = (
                            session.get(
                                TakeStopOrder,
                                (last_record.take_id, last_record.exchange),
                            )
                            if last_record.take_id
                            else None
                        )
                        tp_price = take_order.price if take_order else None
                        is_tp_hit = (
                            tp_price
                            and abs(trade["price"] - tp_price) / tp_price < 0.0005
                        )

                        exit_order = GeneralOrder(
                            id=trade_id,
                            exchange=active_exchange,
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

        finally:
            session.close()

    return symbol_status


def manage_open_limit(client):
    typ = "limit"
    trading_config = trading.watcher.get_config()
    active_exchange = trading_config.exchange

    for symbol in trading_config.list_of_interest:
        current_open = fetch.get_open_orders(symbol)

        for x in current_open:
            if x.get("reduceOnly") is True or x.get("status") == "filled":
                continue

            api_order_id = x.get("id")
            if api_order_id is None:
                continue
            order_id = str(api_order_id)

            with SessionLocal() as session:
                old_order = (
                    session.execute(
                        select(GeneralOrder).where(
                            GeneralOrder.id == order_id,
                            GeneralOrder.exchange == active_exchange,
                        )
                    )
                    .scalars()
                    .first()
                )
                if not old_order:
                    continue

                s = x.get("side", "").lower()
                info = x.get("info") or {}
                amount_value = x.get("amount")
                if amount_value is None:
                    amount_value = info.get("origQty")
                try:
                    order_amount = float(amount_value)
                except (TypeError, ValueError):
                    logger.warning(
                        f"Skipping order {order_id}: invalid amount {amount_value!r}"
                    )
                    continue

                executed_value = x.get("filled")
                if executed_value is None:
                    executed_value = x.get("executedQty")
                if executed_value is None:
                    executed_value = info.get("executedQty")
                if executed_value is None and x.get("remaining") is not None:
                    try:
                        executed_value = order_amount - float(x["remaining"])
                    except (TypeError, ValueError):
                        executed_value = 0
                try:
                    executed_amount = float(executed_value or 0)
                except (TypeError, ValueError):
                    logger.warning(
                        f"Skipping order {order_id}: invalid executed quantity "
                        f"{executed_value!r}"
                    )
                    continue

                remaining_amount = max(order_amount - executed_amount, 0.0)
                if remaining_amount <= 0:
                    continue

                try:
                    # 1. Exchange Action
                    cancel_result = std_call(
                        client.cancel_order, id=order_id, symbol=symbol
                    )

                    # The order may fill more while cancellation is in flight.
                    cancel_info = (
                        cancel_result.get("info") or {}
                        if isinstance(cancel_result, dict)
                        else {}
                    )
                    cancel_filled = (
                        cancel_result.get("filled")
                        if isinstance(cancel_result, dict)
                        else None
                    )
                    if cancel_filled is None and isinstance(cancel_result, dict):
                        cancel_filled = cancel_result.get("executedQty")
                    if cancel_filled is None:
                        cancel_filled = cancel_info.get("executedQty")
                    if cancel_filled is not None:
                        executed_amount = max(executed_amount, float(cancel_filled))
                        remaining_amount = max(order_amount - executed_amount, 0.0)
                    if remaining_amount <= 0:
                        continue

                    p = rm.blp(symbol, s, remaining_amount)

                    new_exchange_order = std_call(
                        client.create_order,
                        symbol=symbol,
                        type=typ,
                        side=s,
                        amount=remaining_amount,
                        price=p,
                    )
                    new_id = str(new_exchange_order["id"])

                    # 2. Create NEW parent first
                    new_order_record = GeneralOrder(
                        id=new_id,
                        exchange=active_exchange,
                        price=new_exchange_order.get("price"),
                        entrance_exit="entrance",
                        # Preserve the original total quantity on the logical
                        # order; the replacement exchange order is only the
                        # still-unfilled quantity.
                        amount=old_order.amount,
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
                        .filter_by(parent_order_id=order_id, exchange=active_exchange)
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

                finally:
                    session.close()
