from sqlalchemy import desc, select

import config.settings as settings
import data.fetch as fetch
from persistance.connection import SessionLocal
from persistance.models import (
    GeneralOrder,
    TakeStopOrder,
)


def manage_open_symbols():
    """
    Checks the DB for active trades and verifies against exchange history.
    If an exit (SL/TP) is found on the exchange, it logs it to SQL.
    """
    symbol_status = {}
    session = SessionLocal()

    try:
        for symbol in settings.list_of_interest:
            # 1. Fetch the most recent local record for this symbol
            stmt = (
                select(GeneralOrder)
                .filter(GeneralOrder.symbol == symbol)
                .order_by(desc(GeneralOrder.time))
            )
            last_record = session.execute(stmt).scalars().first()

            # Logic: If no record exists or last was an exit, symbol is ready.
            if not last_record or last_record.entrace_exit == "exit":
                symbol_status[symbol] = "open"
                continue

            # 2. We have an 'entrance' without a local 'exit'. Check the Exchange.
            # We fetch recent trades to see if our SL or TP was triggered.
            exchange_trades = fetch.get_orders(symbol, limit=5)

            is_now_closed = False
            for trade in exchange_trades:
                # Compare exchange price to our linked Take/Stop prices
                # We use a small tolerance (0.01%) to account for float precision
                tp_price = (
                    last_record.take_order.price if last_record.take_order else None
                )
                sl_price = (
                    last_record.stop_order.price if last_record.stop_order else None
                )

                # Check if this trade matches our TP or SL price
                hit_tp = tp_price and abs(trade["price"] - tp_price) / tp_price < 0.0001
                hit_sl = sl_price and abs(trade["price"] - sl_price) / sl_price < 0.0001

                if hit_tp or hit_sl:
                    # 3. Create the Exit record in GeneralOrder
                    exit_order = GeneralOrder(
                        id=trade["id"],
                        entrace_exit="exit",
                        price=trade["price"],
                        amount=trade["amount"],
                        side="sell" if last_record.side == "buy" else "buy",
                        symbol=symbol,
                        order_type="limit" if hit_tp else "market",
                        time=trade["timestamp"],
                        previous_time=last_record.time,  # Linking to the entrance
                    )
                    session.add(exit_order)
                    is_now_closed = True
                    break

            if is_now_closed:
                session.commit()
                symbol_status[symbol] = "open"
            else:
                # Still in the trade, no exit found on exchange yet
                symbol_status[symbol] = "closed"

    except Exception as e:
        session.rollback()
        print(f"Error syncing {symbol}: {e}")
    finally:
        session.close()

    return symbol_status
