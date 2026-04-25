from loguru import logger

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg
from config import risk, settings

def avaliation_and_place(client):
    # Load configurations once outside the loop for performance
    trading_config = settings.TradingConfig()
    risk_threshold = risk.RiskConfig().acceptable_confidence

    open_closed = pm.manage_open_symbols()
    logger.info(f"Processing markets: {open_closed}")

    for symbol, status in open_closed.items():
        if status == "closed":
            continue
            logger.info(f"Skipped {symbol}")

        # 1. Market Evaluation
        market_data = sg.avaliation_of_market(symbol, trading_config.list_of_parameters)

        confidence = market_data.get("confidence")
        side = market_data.get("regime")  # Assuming 'regime' or 'direction' maps to 's'

        # Validation Checks
        if confidence < risk_threshold:
            logger.debug(f"Skipping {symbol}: Low confidence ({confidence})")
            continue

        if side == "neutral":
            continue

        # 2. Risk & Pricing Calculations
        stop_loss, take_profit, _ = sg.get_loss_and_profit_stops(symbol, side)

        amount = risk_manager.smart_amount(symbol)

        if amount < 0.01:
            logger.info(
                f"Execution skipped for {symbol}: Amount {amount} below safety constraints."
            )
            continue

        entry_price = risk_manager.blp(symbol, side, amount)

        # 3. Execution
        try:
            order_manager.order(
                client,
                symbol,
                trading_config.execution_order,
                side,
                amount,
                entry_price,
                stop_loss,
                take_profit
            )
            logger.info(f"Order placed successfully for {symbol}")
        except Exception as e:
            logger.error(f"Failed to place order for {symbol}: {e}")

    logger.info("Placement cycle completed")
