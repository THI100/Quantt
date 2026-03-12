from sqlalchemy import desc, select

import config.settings as settings
import data.fetch as fetch
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
                symbol, limit=10
            )  # Increased limit for safety
            is_now_closed_on_exchange = False

            for trade in exchange_trades:
                # Get target prices from the linked tables
                tp_price = (
                    last_record.take_order.price if last_record.take_order else None
                )
                sl_price = (
                    last_record.stop_order.price if last_record.stop_order else None
                )

                # Matching logic with 0.01% tolerance
                hit_tp = tp_price and abs(trade["price"] - tp_price) / tp_price < 0.0001
                hit_sl = sl_price and abs(trade["price"] - sl_price) / sl_price < 0.0001

                if hit_tp or hit_sl:
                    # Create the missing Exit record
                    exit_order = GeneralOrder(
                        id=trade["id"],
                        entrace_exit="exit",  # Matches your state logic
                        price=trade["price"],
                        amount=trade["amount"],
                        side="sell" if last_record.side == "buy" else "buy",
                        symbol=symbol,
                        order_type="limit" if hit_tp else "market",
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
        print(f"Error syncing {symbol}: {e}")
    finally:
        session.close()

    return symbol_status
