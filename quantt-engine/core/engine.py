import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg
from config import risk, settings


def avaliation_and_place():
    open_closed = pm.manage_open_symbols()
    print(open_closed)

    for market, status in open_closed.items():
        if status == "open":
            symbol = market
            data = sg.get_overall_market_signal(symbol)
            s = data[3]

            if data[0] < risk.acceptable_confidence:
                continue

            if s == "neutral":
                continue

            data2 = sg.get_loss_and_profit_stops(symbol, s)

            ls = data2[0]
            tp = data2[1]
            p = data2[2]
            nn = risk_manager.smart_amount(symbol)

            if nn < 0.01:
                nn = 0.01

            print(f"This value: {tp} has this porcentage of being achieved {data[1]}.")

            order_manager.order(symbol, "market", s, nn, p, ls, tp)

        else:
            continue

    print("placement completed")
