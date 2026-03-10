from asyncio.windows_events import SelectorEventLoop

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg


def avaliation_and_place():
    open_closed = pm.manage_open_symbols()
    print(open_closed)

    for symbol, status in open_closed.items():
        if status == "open":
            marker = symbol
            data = sg.get_overall_market_signal(marker)
            s = data[3]
            data2 = sg.get_loss_and_profit_stops(marker, s)
            s_temp = data2[3]
            s = s_temp

            ls = data2[0]
            tp = data2[1]
            p = data2[2]
            nn = risk_manager.smart_amount(marker)
            if nn < 0.01:
                nn = 0.01

            order_manager.order(marker, "market", s, nn, p, ls, tp)

        else:
            continue

    print("placement completed")
