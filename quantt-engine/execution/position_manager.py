import asyncio

from loguru import logger
from sqlalchemy import desc, select

import config.settings as settings
import data.fetch as fetch
from execution import risk_manager as rm
from persistance.connection import SessionLocal
from persistance.models import GeneralOrder, TakeStopOrder


async def manage_open_symbols():
    symbol_status = {}

    async def process_symbol(symbol):
        # 1. DB Fetch (Wrapped in thread)
        def get_last_rec():
            with SessionLocal() as session:
                stmt = (
                    select(GeneralOrder)
                    .filter(GeneralOrder.symbol.like(f"{symbol}%"))
                    .order_by(desc(GeneralOrder.time))
                )
                return session.execute(stmt).scalars().first()

        last_record = await asyncio.to_thread(get_last_rec)

        if not last_record or last_record.entrance_exit == "exit":
            return symbol, "open"

        # 2. Network Fetch (Awaited)
        exchange_trades = await fetch.get_orders(symbol, limit=2)
        is_now_closed = False

        def sync_exit_logic(trades, rec):
            with SessionLocal() as session:
                for trade in trades:
                    is_opp = trade["side"].lower() != rec.side.lower()
                    is_red = trade.get("info", {}).get("reduceOnly") in [
                        True,
                        "true",
                        "True",
                    ]
                    is_after = trade["timestamp"] > rec.time

                    if is_opp and (is_red and is_after):
                        exists = (
                            session.execute(
                                select(GeneralOrder).filter(
                                    GeneralOrder.id == str(trade["id"])
                                )
                            )
                            .scalars()
                            .first()
                        )

                        if exists:
                            return True

                        # Calculate if TP was hit
                        tp_p = rec.take_order.price if rec.take_order else None
                        is_tp = tp_p and abs(trade["price"] - tp_p) / tp_p < 0.0005

                        exit_order = GeneralOrder(
                            id=str(trade["id"]),
                            entrance_exit="exit",
                            price=trade["price"],
                            amount=trade["amount"],
                            side=trade["side"].lower(),
                            symbol=rec.symbol,
                            order_type="limit" if is_tp else "market",
                            time=trade["timestamp"],
                            previous_time=rec.time,
                        )
                        session.add(exit_order)
                        session.commit()
                        return True
                return False

        is_now_closed = await asyncio.to_thread(
            sync_exit_logic, exchange_trades, last_record
        )
        return symbol, "open" if is_now_closed else "closed"

    # Run all symbol checks in parallel
    results = await asyncio.gather(
        *(process_symbol(s) for s in settings.list_of_interest)
    )
    return dict(results)


async def manage_open_limit(client):
    typ = "limit"

    async def update_limit(symbol):
        current_open = await fetch.get_open_orders(symbol, 10)

        for x in current_open:
            if x.get("reduceOnly") is True or x.get("status") == "filled":
                continue

            order_id = x.get("id")
            side = x.get("side").lower()
            amt = x.get("amount")

            # Risk calculation (Assuming rm.blp is now async)
            p = await rm.blp(symbol, side, amt)

            def sync_db_migration(old_id, new_data):
                with SessionLocal() as session:
                    try:
                        old_order = session.get(GeneralOrder, old_id)
                        new_rec = GeneralOrder(
                            id=new_data["id"],
                            price=new_data.get("price"),
                            entrance_exit="entrance",
                            amount=new_data.get("amount", amt),
                            side=new_data.get("side"),
                            symbol=symbol,
                            order_type=typ,
                            time=new_data.get("timestamp"),
                            previous_time=new_data.get("lastTradeTimestamp"),
                        )
                        session.add(new_rec)

                        children = (
                            session.query(TakeStopOrder)
                            .filter(TakeStopOrder.parent_order_id == old_id)
                            .all()
                        )
                        for child in children:
                            child.parent_order_id = new_data["id"]

                        if old_order:
                            session.delete(old_order)
                        session.commit()
                    except Exception as e:
                        session.rollback()
                        logger.error(e)

            try:
                await client.cancel_order(order_id, symbol)
                new_ex_order = await client.create_order(symbol, typ, side, amt, p)
                await asyncio.to_thread(sync_db_migration, order_id, new_ex_order)
                logger.info(f"Re-priced {symbol} limit order to {p}")
            except Exception as e:
                logger.error(f"Failed to move limit for {symbol}: {e}")

    # Process all symbol limit updates in parallel
    await asyncio.gather(*(update_limit(s) for s in settings.list_of_interest))
