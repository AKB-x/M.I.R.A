
import json
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

app = FastAPI(
    title="M.I.R.A.",
    description="Market Intelligence and Risk Analysis API",
    version="1.0.0"
)

# Folder containing processed market data
DATA_DIR = Path(__file__).resolve().parent / "data" / "processed"

SUPPORTED_ASSETS = ["SPY", "GLD"]


# 1. Health check
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "M.I.R.A."
    }


# 2. Supported assets
@app.get("/assets")
def get_assets():
    return {
        "assets": SUPPORTED_ASSETS,
        "count": len(SUPPORTED_ASSETS)
    }


# 3. Latest analytics for an asset
@app.get("/analytics/{symbol}")
def get_analytics(symbol: str):

    symbol = symbol.upper()

    if symbol not in SUPPORTED_ASSETS:
        raise HTTPException(
            status_code=404,
            detail="Asset not supported"
        )

    file_path = DATA_DIR / f"{symbol}_returns.csv"

    if not file_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Analytics data unavailable"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise HTTPException(
            status_code=503,
            detail="Analytics data is empty"
        )

    latest = df.iloc[-1]

    return {
        "symbol": symbol,
        "date": str(latest["Date"]),
        "adj_close": round(float(latest["adj_close"]), 2),
        "daily_return": round(float(latest["daily_return"]), 4),
        "rsi_14": round(float(latest["rsi_14"]), 2),
        "sma_20": round(float(latest["sma_20"]), 2),
        "ema_20": round(float(latest["ema_20"]), 2),
        "annualized_volatility_20d": round(
            float(latest["annualized_volatility_20d"]), 4
        )
    }


# 4. Get all alerts
@app.get("/alerts")
def get_alerts():

    file_path = DATA_DIR / "alerts.json"

    if not file_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Alert data unavailable"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        alerts = json.load(file)

    return {
        "total": len(alerts),
        "alerts": alerts[:50]
    }


# 5. Get alerts for a specific asset
@app.get("/alerts/{symbol}")
def get_asset_alerts(symbol: str):

    symbol = symbol.upper()

    if symbol not in SUPPORTED_ASSETS:
        raise HTTPException(
            status_code=404,
            detail="Asset not supported"
        )

    file_path = DATA_DIR / "alerts.json"

    if not file_path.exists():
        raise HTTPException(
            status_code=503,
            detail="Alert data unavailable"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        alerts = json.load(file)

    asset_alerts = [
        alert for alert in alerts
        if alert["symbol"] == symbol
    ]

    return {
        "symbol": symbol,
        "total": len(asset_alerts),
        "alerts": asset_alerts[:50]
    }
