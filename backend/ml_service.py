"""
ml_service.py
-------------
Backend module that trains a Linear Regression model on the
fetched stock data and produces future price estimates.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def train_prediction_model(data: pd.DataFrame):
    """
    Trains a simple Linear Regression model (Close price vs day index)
    on an 80/20 train-test split.

    Returns:
        model, X_test, y_test, predictions, mae, rmse, r2
    """
    df = data.copy()
    df["Day"] = np.arange(len(df))

    X = df[["Day"]]
    y = df["Close"].values

    split_index = int(len(df) * 0.80)

    if split_index < 10:
        raise ValueError(
            "Not enough historical data to train a model. "
            "Pick a longer period (e.g. 1y or 2y)."
        )

    X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
    y_train, y_test = y[:split_index], y[split_index:]

    model = LinearRegression()
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    r2 = r2_score(y_test, predictions)

    return model, X_test, y_test, predictions, mae, rmse, r2


def predict_future_prices(model: LinearRegression, data: pd.DataFrame, days: int) -> pd.DataFrame:
    """
    Projects the trend forward by `days` business days.
    """
    last_day = len(data) - 1

    future_days = np.arange(last_day + 1, last_day + days + 1).reshape(-1, 1)
    predictions = model.predict(future_days)

    future_dates = pd.date_range(
        start=data["Date"].iloc[-1] + pd.Timedelta(days=1),
        periods=days,
        freq="B",
    )

    return pd.DataFrame({"Date": future_dates, "Predicted Price": predictions})
