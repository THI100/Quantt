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

                db_symbol_name = last_record.symbol

                if hit_tp or hit_sl:
                    # 1. Check if this specific exchange ID is already in our DB
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
                        # If it exists, it means the trade is already logged as an exit
                        is_now_closed = True
                        break

                    # 2. If it doesn't exist, create the Exit record
                    exit_order = GeneralOrder(
                        id=str(trade["id"]),
                        entrance_exit="exit",
                        price=trade["price"],
                        amount=trade["amount"],
                        side="sell" if last_record.side == "buy" else "buy",
                        symbol=last_record.symbol,  # Use the symbol exactly as it is in the DB
                        order_type="limit" if hit_tp else "market",
                        time=trade["timestamp"],
                        previous_time=last_record.time,
                    )
                    session.add(exit_order)
                    is_now_closed = True
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
