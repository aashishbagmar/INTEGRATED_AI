# services/price_service.py

import pandas as pd
import numpy as np
import datetime
import pandas_datareader.data as web

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


def _load_price_data(symbol: str):
    """
    Load historical stock data using STOOQ (Yahoo replacement)
    """
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=365 * 5)

    try:
        df = web.DataReader(symbol, "stooq", start, end)
    except Exception as e:
        print(f"❌ Data fetch error: {e}")
        return None

    if df.empty:
        return None

    # Stooq returns newest first → reverse
    df = df.sort_index()
    return df

# def _load_price_data(symbol: str):
#     """
#     Load historical stock data for Indian market using Yahoo Finance
#     """
#     symbol = symbol.upper()

#     # Auto-append NSE if not provided
#     if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
#         symbol = f"{symbol}.NS"

#     end = datetime.datetime.now()
#     start = end - datetime.timedelta(days=365 * 5)

#     df = yf.download(
#         symbol,
#         start=start,
#         end=end,
#         interval="1d",
#         progress=False
#     )

#     if df.empty:
#         return None

#     return df



def _train_models(df):
    """
    Train Linear Regression + Random Forest
    """
    df = df.copy()
    df["Day"] = np.arange(len(df))

    X = df[["Day"]].values
    y = df["Close"].values

    lr = LinearRegression()
    lr.fit(X, y)

    rf = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )
    rf.fit(X, y)

    return lr, rf


def get_price_forecast(symbol: str):
    """
    Main price forecasting service (AI-based)
    """
    symbol = symbol.strip().upper()

    print(f"\n📡 Fetching price data for {symbol} (STOOQ)...")

    df = _load_price_data(symbol)
    if df is None:
        print("❌ Price data fetch failed")
        return None

    lr, rf = _train_models(df)

    last_day = len(df)
    future_day = last_day + 30  # 30-day forecast

    lr_pred = lr.predict([[future_day]])[0]
    rf_pred = rf.predict([[future_day]])[0]

    predicted_price = (lr_pred + rf_pred) / 2
    current_price = df["Close"].iloc[-1]

    returns = df["Close"].pct_change().dropna()
    volatility = returns.std() * 100

    trend_pct = ((predicted_price - current_price) / current_price) * 100

    if trend_pct > 3:
        signal = "Bullish"
    elif trend_pct < -3:
        signal = "Bearish"
    else:
        signal = "Neutral"
    # --------------------------------------------------
    # RETURN (used by decision engine)
    # --------------------------------------------------
    return {
        "symbol": symbol,
        "current_price": round(float(current_price), 2),
        "predicted_price": round(float(predicted_price), 2),
        "trend_pct": round(float(trend_pct), 2),
        "volatility": round(float(volatility), 2),
        "signal": signal
    }
