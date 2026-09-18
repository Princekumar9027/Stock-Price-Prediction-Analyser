"""
data_service.py
----------------
Backend module responsible for pulling REAL, live stock data
from Yahoo Finance via yfinance. No mock/demo data is used here -
every call hits Yahoo Finance's servers directly.
"""

import pandas as pd
import yfinance as yf


def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """
    Fetch live historical stock data for a given symbol.

    Args:
        symbol: Stock ticker, e.g. "AAPL", "RELIANCE.NS"
        period: One of "1mo", "3mo", "6mo", "1y", "2y", "5y"

    Returns:
        Cleaned pandas DataFrame with Date, Open, High, Low, Close, Volume
    """
    symbol = str(symbol).strip().upper()

    if not symbol:
        raise ValueError("Please enter a stock symbol.")

    try:
        data = yf.download(
            symbol,
            period=period,
            progress=False,
            auto_adjust=False,
        )
    except Exception as e:
        raise ValueError(f"Unable to reach Yahoo Finance: {str(e)}")

    if data.empty:
        raise ValueError(
            f"No data found for '{symbol}'. Check the ticker symbol "
            "(Indian stocks need a '.NS' suffix, e.g. TCS.NS)."
        )

    # yfinance sometimes returns MultiIndex columns - flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data = data.reset_index()

    required_columns = ["Date", "Open", "High", "Low", "Close", "Volume"]
    missing = [c for c in required_columns if c not in data.columns]
    if missing:
        raise ValueError(f"Yahoo Finance response is missing: {', '.join(missing)}")

    data = data[required_columns].copy()

    for col in ["Open", "High", "Low", "Close", "Volume"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna()

    if data.empty:
        raise ValueError("Stock data came back empty after cleaning.")

    return data
