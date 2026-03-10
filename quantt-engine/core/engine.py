import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg


def avaliation_and_place():
    o_c = pm.manage_open_symbols()

    for oc in o_c:
        if oc == "open":
            marker = oc
            data = sg.get_overall_market_signal(marker)
            s = data[3]
            data2 = sg.get_loss_and_profit_stops(marker, s)

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
