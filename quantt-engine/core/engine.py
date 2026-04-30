import math

from loguru import logger

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg
from config import risk, settings
from data import fetch


def avaliation_and_place(client):
    trading_config = settings.watcher.get_config()
    risk_cfg = risk.watcher.get_config()

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
            logger.info(f"{symbol} is in the state of {side} market.")
            continue

        conf_score = data["confidence"] * 100  # Transforming to %
        if conf_score < risk_cfg.acceptable_confidence:
            logger.debug(
                f"Skipping {symbol}: Confidence {conf_score:.2f} below threshold."
            )
            continue

        # Regime-specific logic
        if data["regime"] == "range" and data["strength"] > 0.8:  # 80% strength
            logger.warning(
                f"High strength ({data['strength']}) detected in range regime for {symbol}. Proceeding with caution."
            )

        stops = sg.get_loss_and_profit_stops(symbol, side)
        sl, tp = stops[0], stops[1]

        # 3. Dynamic Sizing based on Strength
        raw_nn = risk_manager.smart_amount(symbol)
        if math.isnan(raw_nn):
            nn = 0.0
        else:
            nn = raw_nn * (0.5 + (data["strength"] / 2))  # Strength based size
            nn = (
                math.floor(nn * 1000) / 1000
            )  # Correcting from any decimal problems. e.g: x.00004

        if nn < 0.01:  # minimum amount for Binance
            logger.info(
                f"Insufficient volume for {symbol}: {nn} is below minimum constraints."
            )
            continue

        # 4. Entry Price Calculation
        entry_price = risk_manager.blp(symbol, side, nn)
        act_price = fetch.get_ticker(symbol)
        act_price = act_price.get("last")

        # 5.1. Minimum Structural Distance Check
        risk_percent_act = abs(act_price - sl) / act_price
        risk_percent = abs(entry_price - sl) / entry_price
        min_dist = 0.003  # 0.3% parameters for the diference between tp and sl.

        if risk_percent and risk_percent_act < min_dist:
            logger.warning(
                f"Skipping {symbol}: SL too tight ({risk_percent:.4f}%, {risk_percent_act:.4f}%). Likely noise."
            )
            continue

        # 5.2. Risk/Reward Check
        current_rrr_act = abs(tp - act_price) / abs(act_price - sl)
        current_rrr = abs(tp - entry_price) / abs(entry_price - sl)
        if current_rrr and current_rrr_act < 1.5:  # Minimum RR
            logger.warning(f"Skipping {symbol}: Poor RR Ratio ({current_rrr:.2f}).")
            continue

        nn = round(nn, 2)
        entry_price = round(entry_price, 4)
        sl = round(sl, 4)
        tp = round(tp, 4)

        valid = sg.is_iceberg(symbol, risk_cfg.maximum_iceberg_share, nn, act_price)
        approval = valid[0]
        nn = valid[1]

        # 6. Execution

        if approval:
            try:
                logger.info(
                    f"Placing {side} order for {symbol} | Conf: {conf_score:.1f}% | Regime: {data['regime']}, | TP: {tp} | SL: {sl}"
                )

                order_manager.execute_iceberg(
                    client,
                    symbol,
                    nn,
                    side,
                    tp,
                    sl,
                )
            except Exception as e:
                logger.error(f"Critical failure executing order for {symbol}: {e}")

        else:
            try:
                logger.info(
                    f"Placing {side} order for {symbol} | Conf: {conf_score:.1f}% | Regime: {data['regime']}, | TP: {tp} | SL: {sl}"
                )

                order_manager.order(
                    client,
                    symbol,
                    trading_config.execution_order,
                    side,
                    nn,
                    entry_price,
                    sl,
                    tp,
                )
            except Exception as e:
                logger.error(f"Critical failure executing order for {symbol}: {e}")

        logger.info("Placement cycle completed")
