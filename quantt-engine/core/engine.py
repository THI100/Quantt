import asyncio

from loguru import logger

import execution.order_manager as order_manager
import execution.position_manager as pm
import execution.risk_manager as risk_manager
import strategy.signal_generator as sg
from config import risk, settings


async def process_market(market: str):
    """Encapsulates the logic for a single symbol to allow parallel execution."""
    try:
        # 1. Get Signal Data
        # Returns: real_confidence, real_strength, actual_movement, direction
        data = await sg.get_overall_market_signal(market)
        direction = data[3]

        # 2. Filters
        if data[0] < risk.acceptable_confidence or direction == "neutral":
            return

        # 3. Get Stop/Profit levels
        # Returns: stop_loss, take_profit, actual_value
        data2 = await sg.get_loss_and_profit_stops(market, direction)
        ls, tp = data2[0], data2[1]

        # 4. Risk & Pricing
        # Assuming smart_amount and blp are now async
        nn = await risk_manager.smart_amount(market)
        nn = max(nn, 0.01)  # Precision safety

        p = await risk_manager.blp(market, direction, nn)

        logger.info(
            f"Symbol: {market} | Direction: {direction} | Confidence: {data[0]}% | TP: {tp}"
        )

        # 5. Place Order
        await order_manager.order(market, "limit", direction, nn, p, ls, tp)

    except Exception as e:
        logger.error(f"Failed to process {market}: {e}")


async def avaliation_and_place():
    # 1. Check all symbol statuses in parallel
    open_closed = await pm.manage_open_symbols()
    logger.info(f"Market Status: {open_closed}")

    # 2. Create tasks only for 'open' symbols
    tasks = [
        process_market(market)
        for market, status in open_closed.items()
        if status == "open"
    ]

    if tasks:
        logger.info(f"Firing analysis and orders for {len(tasks)} symbols...")
        # 3. This is where the magic happens: everything runs at once
        await asyncio.gather(*tasks)

    logger.info("Placement cycle completed")
