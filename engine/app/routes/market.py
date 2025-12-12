# app/routes/market.py
from fastapi import APIRouter, HTTPException
from app.services.exchange import get_OHLCV, get_ticker

router = APIRouter(prefix="/market", tags=["market"])

@router.get("/ticker/")
async def ticker(symbol: str):
    """
    Example:
      GET /market/ticker/?symbol=BTC/USDT
    (symbol must be URL-encoded if needed)
    """
    try:
        data = get_ticker(symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    
@router.get("/ohlcv/")
async def ohlcv(symbol: str):
    """
    Example:
      GET /market/ohlcv/?symbol=BTC/USDT
    (symbol must be URL-encoded if needed)
    """
    try:
        data = get_OHLCV(symbol)
        return data
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))