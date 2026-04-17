from loguru import logger

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg
from config import risk


def avaliation_and_place(client):
    open_closed = pm.manage_open_symbols()
    logger.info(open_closed)

    for market, status in open_closed.items():
        if status == "open":
            symbol = market
            data = sg.get_overall_market_signal(symbol)
            s = data[3]

            if data[0] < risk.RiskConfig().acceptable_confidence:
                continue

            if s == "neutral":
                continue

            data2 = sg.get_loss_and_profit_stops(symbol, s)

            ls = data2[0]
            tp = data2[1]
            nn = risk_manager.smart_amount(symbol)
            p = risk_manager.blp(symbol, s, nn)

            # if p <= ls or p >= tp:
            #     logger.info(
            #         f"Seems like this possible order would return a error... as its price is bigger than take profit or lower than stop loss."
            #     )
            #     continue

            if nn < 0.01:
                logger.info(
                    f"Is not feasible or safe to execute a order in {market}, due to low amount and constrains."
                )
                continue

            order_manager.order(client, symbol, "limit", s, nn, p, ls, tp)

        else:
            continue

    logger.info("placement completed")
