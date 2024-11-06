from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import pandas as pd
import requests
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware to allow requests from localhost:5500 (your frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalysisResult(BaseModel):
    max_price: float
    min_price: float
    closing_price: float
    trend: str
    avg_price: float
    price_change: float
    volume_avg: float


def fetch_data(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
    }
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(
        data,
        columns=[
            "timestamp",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base_asset_volume",
            "taker_buy_quote_asset_volume",
            "ignore",
        ],
    )

    # Convert timestamp from milliseconds to a string for JSON serialization
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms").astype(str)
    df["open"] = pd.to_numeric(df["open"], errors="coerce")
    df["high"] = pd.to_numeric(df["high"], errors="coerce")
    df["low"] = pd.to_numeric(df["low"], errors="coerce")
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    return df


def analyze_data(data):
    max_price = data["high"].max()
    min_price = data["low"].min()
    closing_price = data["close"].iloc[-1]
    trend = (
        "Uptrend"
        if closing_price > data["close"].iloc[0]
        else "Downtrend" if closing_price < data["close"].iloc[0] else "Sideways"
    )
    avg_price = data["close"].mean()
    price_change = (
        (closing_price - data["close"].iloc[0]) / data["close"].iloc[0]
    ) * 100
    volume_avg = data["volume"].mean()

    return AnalysisResult(
        max_price=max_price,
        min_price=min_price,
        closing_price=closing_price,
        trend=trend,
        avg_price=avg_price,
        price_change=price_change,
        volume_avg=volume_avg,
    )


@app.get("/fetch_crypto_data")
def get_crypto_data():
    symbol = "BTCUSDT"
    interval = "1d"
    start_time = "1693593600000"  # September 1, 2024
    end_time = "1696272000000"  # October 1, 2024

    data = fetch_data(symbol, interval, start_time, end_time)
    return JSONResponse(content=data.to_dict(orient="records"))


@app.get("/analyze_crypto_data")
def get_analysis():
    symbol = "BTCUSDT"
    interval = "1d"
    start_time = "1693593600000"  # September 1, 2024
    end_time = "1696272000000"  # October 1, 2024

    data = fetch_data(symbol, interval, start_time, end_time)
    analysis = analyze_data(data)
    return analysis


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
