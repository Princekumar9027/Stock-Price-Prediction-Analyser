"""
chart_service.py
-----------------
Backend module that builds the Plotly charts used by the frontend.
"""

import pandas as pd
import plotly.graph_objects as go


def create_price_graph(data: pd.DataFrame, symbol: str) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            mode="lines",
            name="Closing Price",
            line=dict(width=2),
        )
    )

    fig.update_layout(
        title=f"{symbol} Historical Closing Price",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        hovermode="x unified",
        height=500,
    )

    return fig


def create_prediction_graph(data: pd.DataFrame, X_test, predictions, symbol: str) -> go.Figure:
    test_dates = data.iloc[X_test.index]["Date"]
    actual_prices = data.iloc[X_test.index]["Close"].values

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=test_dates, y=actual_prices, mode="lines", name="Actual Price"))
    fig.add_trace(go.Scatter(x=test_dates, y=predictions, mode="lines", name="Predicted Price"))

    fig.update_layout(
        title=f"{symbol} Actual vs Predicted Price",
        xaxis_title="Date",
        yaxis_title="Price",
        template="plotly_white",
        hovermode="x unified",
        height=500,
    )

    return fig
