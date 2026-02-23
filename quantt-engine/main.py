import data.cache as cache
import data.fetch as fetch
import strategy.indicators as indicators
import strategy.signal_generator as sg
from execution import order_manager, risk_manager

marker = "BTC/USDT"
data = sg.get_overall_market_signal(marker)
s = data[3]
data2 = sg.get_loss_and_profit_stops(marker, s)

ls = data2[0]
tp = data2[1]
p = data2[2]
nn = risk_manager.smart_amount(marker)
print(f"{s}, {ls}, {tp}, {p}, {nn}")

ord = order_manager.order(marker, "market", s, 0.01, p, ls, tp)

print(
    f"Entry: \n{ord[0]}. \n take profit order: \n{ord[1]}. \n stop loss order: \n{ord[2]}"
)
