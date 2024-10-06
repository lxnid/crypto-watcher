import requests
import pandas as pd
import matplotlib.pyplot as plt


def fetch_data(symbol, interval, start_time, end_time):
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol,
        "interval": interval,
        "startTime": start_time,
        "endTime": end_time,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
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
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()


def analyze_data(data):
    # Ensure the relevant columns are converted to numeric values
    data["high"] = pd.to_numeric(data["high"], errors="coerce")
    data["low"] = pd.to_numeric(data["low"], errors="coerce")
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data["volume"] = pd.to_numeric(data["volume"], errors="coerce")

    # Check if data is empty after conversion
    if data.empty:
        return {"error": "No data to analyze"}

    # Calculate key metrics
    max_price = data["high"].max()
    min_price = data["low"].min()
    closing_price = data["close"].iloc[-1]

    # Determine trend
    trend = (
        "Uptrend"
        if closing_price > data["close"].iloc[0]
        else "Downtrend" if closing_price < data["close"].iloc[0] else "Sideways"
    )

    # Calculate average price and percentage change
    avg_price = data["close"].mean()
    price_change = (
        (closing_price - data["close"].iloc[0]) / data["close"].iloc[0]
    ) * 100

    # Calculate average volume
    volume_avg = data["volume"].mean()

    return {
        "max_price": max_price,
        "min_price": min_price,
        "closing_price": closing_price,
        "trend": trend,
        "avg_price": avg_price,
        "price_change": price_change,
        "volume_avg": volume_avg,
    }


def visualize_data(data):
    if not data.empty:
        plt.figure(figsize=(12, 6))
        plt.plot(data["timestamp"], data["close"])
        plt.title("Daily Closing Price")
        plt.xlabel("Timestamp")
        plt.ylabel("Price")
        plt.show()
    else:
        print("No data to visualize")


if __name__ == "__main__":
    symbol = "BTCUSDT"
    interval = "1d"
    # in unix time format - time in milli seconds from Jan 1, 1970
    start_time = "1693593600000"  # September 1, 2024
    end_time = "1728187056238"  # October 6, 2024

    data = fetch_data(symbol, interval, start_time, end_time)
    analysis = analyze_data(data)
    visualize_data(data)

    print(analysis)
