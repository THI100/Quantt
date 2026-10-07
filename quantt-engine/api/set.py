from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from config import risk, trading
from core.bot import TradingBot
from exchange.awm import ensure_env_file, remove_env_file, write_api_credentials

s_route = APIRouter()
bot = TradingBot()


class APIConfig(BaseModel):
    api_key: str
    api_secret: str
    exchange: str


# ------------------------------------------------------------------ #
#  Config — trading                                                    #
# ------------------------------------------------------------------ #


@s_route.get("/config/trading", response_model=trading.TradingConfigPYD)
def get_trading_config(profile_name: str = "base"):
    """Return a trading configuration profile."""
    try:
        return trading.load_trading_config(profile_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@s_route.get("/config/trading/profiles", response_model=list[str])
def get_trading_profiles():
    try:
        return trading.list_trading_profiles()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@s_route.put("/config/trading", response_model=trading.TradingConfigPYD)
def update_trading_config(new_cfg: trading.TradingConfigPYD):
    """Create or update the profile named in the request body."""
    error = trading.save_trading_config(new_cfg)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return new_cfg


@s_route.patch("/config/trading", response_model=trading.TradingConfigPYD)
def patch_trading_config(partial: dict, profile_name: str = "base"):
    """Partially update the trading configuration (only provided fields change)."""
    current = trading.load_trading_config(profile_name)
    if "name" in partial and partial["name"] != profile_name:
        raise HTTPException(status_code=400, detail="Profile name cannot be changed")
    updated = current.model_copy(update=partial)
    error = trading.save_trading_config(updated)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return updated


@s_route.delete("/config/trading/{profile_name}")
def delete_trading_config(profile_name: str):
    error = trading.delete_trading_config(profile_name)
    if error:
        status = 404 if "not found" in error.lower() else 500
        raise HTTPException(status_code=status, detail=error)
    return {"message": f"Trading profile '{profile_name}' deleted"}


# ------------------------------------------------------------------ #
#  Config — risk                                                       #
# ------------------------------------------------------------------ #


@s_route.get("/config/risk", response_model=risk.RiskConfigPYD)
def get_risk_config(profile_name: str = "base"):
    """Return a risk configuration profile."""
    try:
        return risk.load_risk_config(profile_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


@s_route.get("/config/risk/profiles", response_model=list[str])
def get_risk_profiles():
    try:
        return risk.list_risk_profiles()
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))


# @s_route.get("/config/store/profiles", response_model=list[str])
# def get_store_profiles():
#     try:
#         return store.list_store_profiles()
#     except RuntimeError as e:
#         raise HTTPException(status_code=500, detail=str(e))


@s_route.put("/config/risk", response_model=risk.RiskConfigPYD)
def update_risk_config(new_cfg: risk.RiskConfigPYD):
    """Create or update the profile named in the request body."""
    error = risk.save_risk_config(new_cfg)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return new_cfg


@s_route.patch("/config/risk", response_model=risk.RiskConfigPYD)
def patch_risk_config(partial: dict, profile_name: str = "base"):
    """Partially update the risk configuration (only provided fields change)."""
    current = risk.load_risk_config(profile_name)
    if "name" in partial and partial["name"] != profile_name:
        raise HTTPException(status_code=400, detail="Profile name cannot be changed")
    updated = current.model_copy(update=partial)
    error = risk.save_risk_config(updated)
    if error:
        raise HTTPException(status_code=500, detail=error)
    return updated


@s_route.delete("/config/risk/{profile_name}")
def delete_risk_config(profile_name: str):
    error = risk.delete_risk_config(profile_name)
    if error:
        status = 404 if "not found" in error.lower() else 500
        raise HTTPException(status_code=status, detail=error)
    return {"message": f"Risk profile '{profile_name}' deleted"}


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


# ------------------------------------------------------------------ #
#  Config — api                                                       #
# ------------------------------------------------------------------ #


@s_route.post("/config/api")
def post_file():
    """
    Directly creates a new .env file if it doesn't exist.
    """
    try:
        return ensure_env_file()
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to initialize .env: {str(e)}"
        )


@s_route.patch("/config/api")
def update_api(config: APIConfig):
    """
    Updates or adds API key and secret for a specific exchange.
    """
    try:
        return write_api_credentials(config.api_key, config.api_secret, config.exchange)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to update API credentials: {str(e)}"
        )


@s_route.delete("/config/api")
def delete_file_route():
    """
    Deletes the entire .env file.
    """
    try:
        result = remove_env_file()
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete configuration: {str(e)}"
        )
