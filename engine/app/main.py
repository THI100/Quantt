# app/main.py
from fastapi import FastAPI
from app.routes import market

app = FastAPI(title="Quant Bot Backend (minimal)")

app.include_router(market.router)

@app.get("/")
async def root():
    return {"status": "backend running"}