from exchange.binance import c_client
import data.fetch as fetch

balance = fetch.get_balance()
print(balance)

