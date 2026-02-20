import data.cache as cache
import data.fetch as fetch
import strategy.indicators as indicators
import strategy.signal_generator as sg
from execution import order_manager, risk_manager

marker = "BTC/USDT"
data = sg.get_overall_market_signal(marker)
data2 = sg.get_loss_and_profit_stops(marker)

s = data[3]
ls = data2[0]
tp = data2[1]
nn = risk_manager.smart_amount(marker)
print(nn)

ord = order_manager.order(marker, "market", s, 0.01, None, ls, tp)

print(ord)
