import config.settings as settings
import data.fetch as fetch


def manage_open_symbols():
    """
    Manage symbols that are open for trade.
    coldown of 1 - 5 minutes.
    """

    symbol_status = {}

    for symbol in settings.list_of_interest:
        val = "open"

        open_orders = fetch.get_orders(symbol)

        symbol_status.update({symbol: val})

    return symbol_status
