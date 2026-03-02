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
        trade_history = fetch.get_orders(symbol, limit=5)

        if not trade_history:
            # If no history exists = open
            symbol_status[symbol] = "open"
            continue



        except (IndexError, AttributeError):
            # Fallback if the data structure is unexpected
            symbol_status[symbol] = "open"

    return symbol_status
