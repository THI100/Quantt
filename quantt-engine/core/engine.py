from loguru import logger
import math

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg
from config import risk, settings

def avaliation_and_place(client):
    trading_config = settings.TradingConfig()
    risk_cfg = risk.RiskConfig()

    # 1. Fetch market states
    open_closed = pm.manage_open_symbols()
    logger.info(f"Market states: {open_closed}")

    for symbol, status in open_closed.items():
        if status != "open":
            continue

        # 2. Market Evaluation
        # data returns: direction, confidence, strength, regime, grades
        data = sg.avaliation_of_market(symbol, trading_config.list_of_parameters)
        side = data["direction"]

        if side == "neutral":
            continue

        conf_score = data["confidence"] * 100
        if conf_score < risk_cfg.acceptable_confidence:
            logger.debug(f"Skipping {symbol}: Confidence {conf_score:.2f} below threshold.")
            continue

        # Regime-specific logic: e.g (If regime is 'range' but momentum grade is too high, it might be a breakout)
        if data["regime"] == "range" and data["strength"] > 0.8:
            logger.warning(f"High strength ({data['strength']}) detected in range regime for {symbol}. Proceeding with caution.")

        stops = sg.get_loss_and_profit_stops(symbol, side)
        sl, tp = stops[0], stops[1]

        # 5. Dynamic Sizing based on Strength
        raw_nn = risk_manager.smart_amount(symbol)
        nn = raw_nn * (0.5 + (data["strength"] / 2))
        nn = math.floor(nn * 1000) / 1000

        if nn < 0.01:
            logger.info(f"Insufficient volume for {symbol}: {nn} is below minimum constraints.")
            continue

        # 6. Entry Price Calculation
        entry_price = risk_manager.blp(symbol, side, nn)

        logger.info(f"Data: {symbol}, {trading_config.execution_order}, {side}, {nn}, {entry_price}, {sl}, {tp}")

        # 7. Execution
        try:
            logger.info(f"Placing {side} order for {symbol} | Conf: {conf_score:.1f}% | Regime: {data['regime']}")
            order_manager.order(
                client,
                symbol,
                trading_config.execution_order,
                side,
                nn,
                entry_price,
                sl,
                tp
            )
        except Exception as e:
            logger.error(f"Critical failure executing order for {symbol}: {e}")

    logger.info("Placement cycle completed")
