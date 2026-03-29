from typing import Optional

from fastapi import APIRouter, HTTPException

from config import risk, settings
from core.bot import TradingBot

s_route = APIRouter()
bot = TradingBot()

# ------------------------------------------------------------------ #
#  Config — trading                                                    #
# ------------------------------------------------------------------ #


@s_route.get("/config/trading", response_model=settings.TradingConfig)
def get_trading_config():
    """Return the current trading configuration."""
    try:
        return settings.load_trading_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@s_route.put("/config/trading", response_model=settings.TradingConfig)
def update_trading_config(new_cfg: settings.TradingConfig):
    """Overwrite the entire trading configuration."""
    settings.save_trading_config(new_cfg)
    return new_cfg


@s_route.patch("/config/trading", response_model=settings.TradingConfig)
def patch_trading_config(partial: dict):
    """Partially update the trading configuration (only provided fields change)."""
    current = settings.load_trading_config()
    updated = current.model_copy(update=partial)
    settings.save_trading_config(updated)
    return updated


# ------------------------------------------------------------------ #
#  Config — risk                                                       #
# ------------------------------------------------------------------ #


@s_route.get("/config/risk", response_model=risk.RiskConfig)
def get_risk_config():
    """Return the current risk configuration."""
    try:
        return risk.load_risk_config()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@s_route.put("/config/risk", response_model=risk.RiskConfig)
def update_risk_config(new_cfg: risk.RiskConfig):
    """Overwrite the entire risk configuration."""
    risk.save_risk_config(new_cfg)
    return new_cfg


@s_route.patch("/config/risk", response_model=risk.RiskConfig)
def patch_risk_config(partial: dict):
    """Partially update the risk configuration (only provided fields change)."""
    current = risk.load_risk_config()
    updated = current.model_copy(update=partial)
    risk.save_risk_config(updated)
    return updated


@s_route.get("/config/risk/limits")
def get_risk_limits(coin: Optional[str]):
    """
    Return derived risk limits computed from the live balance.
    Requires an exchange call to fetch current account balance.
    TODO: replace bot.get_balance() with your actual exchange balance method.
    """
    try:
        cfg = risk.load_risk_config()
        balance = bot.check_bal()

        if coin == "usdt":
            b = balance[0]
            mps = b["total"] * cfg.percentage_of_capital_per_trade
            mte = b["total"] * cfg.maximum_loss
            mlpt = mps * cfg.maximum_loss

        elif coin == "usdc":
            b = balance[1]
            mps = b["total"] * cfg.percentage_of_capital_per_trade
            mte = b["total"] * cfg.maximum_loss
            mlpt = mps * cfg.maximum_loss

        else:
            b = balance
            for c in balance:
                mps = c["total"] * cfg.percentage_of_capital_per_trade
                mte = c["total"] * cfg.maximum_loss
                mlpt = mps * cfg.maximum_loss

        return {
            "balance": b,
            "max_position_size": mps,
            "max_total_exposure": mte,
            "max_loss_per_trade": mlpt,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to compute risk limits: {str(e)}"
        )
