from asyncio.windows_events import SelectorEventLoop

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg


def avaliation_and_place():
    open_closed = pm.manage_open_symbols()
    print(open_closed)

    for market, status in open_closed.items():
        if status == "open":
            symbol = market
            data = sg.get_overall_market_signal(symbol)
            s = data[3]

            if s == "neutral":
                continue

            data2 = sg.get_loss_and_profit_stops(symbol, s)

            ls = data2[0]
            tp = data2[1]
            p = data2[2]
            nn = risk_manager.smart_amount(symbol)

            if nn < 0.01:
                nn = 0.01

            print(f"{ls}, {tp}, {p}, {nn}, {symbol}")

            order_manager.order(symbol, "market", s, nn, p, ls, tp)

        else:
            continue

    print("placement completed")
