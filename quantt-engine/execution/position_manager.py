import config.settings as settings
import data.fetch as fetch


def manage_open_symbols():
    """
    Determines symbol status by checking the most recent filled trade.
    'open' = Ready for new trade (Last trade was an Exit).
    'closed' = Already in a trade (Last trade was an Entry).
    """
    symbol_status = {}

    for symbol in settings.list_of_interest:
        # Fetch the most recent FILLED orders (trade history)
        # We usually only need the last 1 or 2 to determine state
        trade_history = fetch.get_orders(symbol, limit=5)

        if not trade_history:
            # If no history exists = open
            symbol_status[symbol] = "open"
            continue

        try:
            # 2. Sort safely. Pyright prefers clear access to keys.
            # We sort descending (newest first)
            sorted_orders = sorted(
                trade_history, key=lambda x: x.get("timestamp", 0), reverse=True
            )
            latest_order = sorted_orders[0]

            # 3. Extract the reduceOnly flag from the nested 'info' dict
            # We use .get() everywhere to prevent KeyErrors
            info = latest_order.get("info", {})

            # Binance API returns 'reduceOnly' as a boolean or a string 'true'/'false'
            is_reduce_only = str(info.get("reduceOnly", "")).lower() == "true"

            if is_reduce_only:
                symbol_status[symbol] = "open"
            else:
                # If the last order was NOT reduceOnly, we are still 'in' the trade
                symbol_status[symbol] = "closed"

        except (IndexError, AttributeError):
            # Fallback if the data structure is unexpected
            symbol_status[symbol] = "open"

    return symbol_status
