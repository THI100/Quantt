import data.cache as cache
import data.fetch as fetch
import execution.order_manager as om
import strategy.indicators as indicators
import strategy.signal_generator as sg

marker = "BTC/USDT"
data = sg.get_overall_market_signal(marker)
data2 = sg.get_loss_and_profit_stops(marker)

s = data[3]
ls = data2[0]
tp = data2[1]

print(f"{ls}, {tp}")
print(data)

ord = om.order(marker, "market", s, 0.002, None, ls, tp)

print(ord)
