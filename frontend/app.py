"""
frontend/app.py
----------------
This file is the FRONTEND ONLY. It builds the Gradio UI: a login/signup
screen first, and the stock analyser screen after a successful login.
It contains no data-fetching, ML, or password-hashing logic itself -
all of that lives in the backend/ package.
"""

import sys
import os

# Make sure the project root is importable regardless of where
# this file is launched from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gradio as gr

from backend.data_service import get_stock_data
from backend.ml_service import train_prediction_model, predict_future_prices
from backend.chart_service import create_price_graph, create_prediction_graph
from backend.user_store import register_user, verify_user

APP_TITLE = "Stock Price Prediction Analyser"


# ============================================================
# MAIN ANALYSIS FUNCTION (glue between UI and backend)
# ============================================================

def analyse_stock(symbol, period, future_days):
    try:
        if not symbol or not str(symbol).strip():
            return ("❌ Please enter a stock symbol.", None, None, None, None)

        future_days = int(future_days)
        future_days = max(1, min(future_days, 30))

        data = get_stock_data(symbol, period)
        symbol = str(symbol).strip().upper()

        historical_graph = create_price_graph(data, symbol)

        model, X_test, y_test, predictions, mae, rmse, r2 = train_prediction_model(data)

        prediction_graph = create_prediction_graph(data, X_test, predictions, symbol)

        future_data = predict_future_prices(model, data, future_days)

        latest_close = float(data["Close"].iloc[-1])
        previous_close = float(data["Close"].iloc[-2]) if len(data) > 1 else latest_close
        change = latest_close - previous_close
        change_percent = (change / previous_close * 100) if previous_close != 0 else 0

        highest_price = float(data["High"].max())
        lowest_price = float(data["Low"].min())
        average_price = float(data["Close"].mean())

        summary = f"""
## 📊 Stock Analysis: {symbol}

**Latest Closing Price:** {latest_close:,.2f}
**Previous Closing Price:** {previous_close:,.2f}
**Daily Change:** {change:,.2f}
**Daily Change %:** {change_percent:.2f}%
**Period High:** {highest_price:,.2f}
**Period Low:** {lowest_price:,.2f}
**Average Closing Price:** {average_price:,.2f}

---

### 🤖 Machine Learning Model

**Algorithm:** Linear Regression &nbsp;|&nbsp; **Train/Test Split:** 80/20
**MAE:** {mae:.4f} &nbsp;|&nbsp; **RMSE:** {rmse:.4f} &nbsp;|&nbsp; **R² Score:** {r2:.4f}

---
⚠️ This is a trend-based ML estimate for learning purposes, not financial advice.
"""

        historical_table = data.tail(50).copy()
        historical_table["Date"] = historical_table["Date"].dt.strftime("%Y-%m-%d")
        for col in ["Open", "High", "Low", "Close"]:
            historical_table[col] = historical_table[col].round(2)

        future_table = future_data.copy()
        future_table["Date"] = future_table["Date"].dt.strftime("%Y-%m-%d")
        future_table["Predicted Price"] = future_table["Predicted Price"].round(2)

        return (summary, historical_graph, historical_table, prediction_graph, future_table)

    except Exception as e:
        return (f"❌ Error: {str(e)}", None, None, None, None)


# ============================================================
# LOGIN / SIGNUP HANDLERS
# ============================================================

def handle_signup(username, password, confirm_password):
    success, message = register_user(username, password, confirm_password)
    return message


def handle_login(username, password):
    success, result = verify_user(username, password)

    if success:
        display_name = result
        welcome = f"### 👋 Welcome, {display_name}!"
        return (
            gr.update(visible=False),   # hide auth screen
            gr.update(visible=True),    # show app screen
            True,                        # logged_in state
            "",                          # clear login error message
            welcome,                     # greeting in app screen
        )
    else:
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            False,
            result,
            "",
        )


def handle_logout():
    return (
        gr.update(visible=True),
        gr.update(visible=False),
        False,
        "",
        "",
    )


# ============================================================
# UI LAYOUT
# ============================================================

custom_css = """
body { background-color: #f5f7fb; }
.gradio-container { max-width: 1200px !important; }
.title { text-align: center; font-size: 32px; font-weight: bold; }
.subtitle { text-align: center; color: #666; }
"""


def build_interface() -> gr.Blocks:
    with gr.Blocks(title=APP_TITLE) as demo:

        logged_in_state = gr.State(False)

        gr.Markdown(
            """
            <div class="title">📈 Stock Price Prediction Analyser</div>
            <div class="subtitle">Live Historical Data + Machine Learning Based Prediction</div>
            """
        )

        # ============================================================
        # AUTH SCREEN (Login / Sign Up)
        # ============================================================

        with gr.Group(visible=True) as auth_group:
            with gr.Tabs():

                with gr.Tab("Login"):
                    login_username = gr.Textbox(label="Username")
                    login_password = gr.Textbox(label="Password", type="password")
                    login_button = gr.Button("🔓 Login", variant="primary")
                    login_message = gr.Markdown("")

                with gr.Tab("Sign Up"):
                    gr.Markdown("Create your own account, no fixed login needed.")
                    signup_username = gr.Textbox(label="Choose a username")
                    signup_password = gr.Textbox(label="Choose a password", type="password")
                    signup_confirm = gr.Textbox(label="Confirm password", type="password")
                    signup_button = gr.Button("📝 Create Account", variant="primary")
                    signup_message = gr.Markdown("")

        # ============================================================
        # APP SCREEN (Stock Analyser) - hidden until login
        # ============================================================

        with gr.Group(visible=False) as app_group:

            greeting = gr.Markdown("")
            logout_button = gr.Button("🚪 Logout")

            gr.Markdown(
                """
                ### 🔍 Enter Stock Details
                Examples: `AAPL` (Apple), `MSFT` (Microsoft), `GOOGL` (Google),
                `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `^NSEI` (NIFTY 50)
                """
            )

            with gr.Row():
                stock_symbol = gr.Textbox(label="Stock Symbol", placeholder="Example: RELIANCE.NS", value="AAPL")
                period = gr.Dropdown(label="Historical Period", choices=["1mo", "3mo", "6mo", "1y", "2y", "5y"], value="1y")
                future_days = gr.Slider(minimum=1, maximum=30, value=7, step=1, label="Prediction Days")

            analyse_button = gr.Button("🔎 Analyse Stock", variant="primary")

            summary_output = gr.Markdown(label="Analysis Summary")

            gr.Markdown("## 📈 Historical Price Chart")
            historical_graph = gr.Plot(label="Historical Price")

            gr.Markdown("## 📋 Historical Data")
            historical_table = gr.Dataframe(label="Recent Historical Data", interactive=False)

            gr.Markdown("## 🤖 Actual vs Predicted")
            prediction_graph = gr.Plot(label="Prediction Performance")

            gr.Markdown("## 🔮 Future Price Prediction")
            future_table = gr.Dataframe(label="Predicted Prices", interactive=False)

            analyse_button.click(
                fn=analyse_stock,
                inputs=[stock_symbol, period, future_days],
                outputs=[summary_output, historical_graph, historical_table, prediction_graph, future_table],
            )

        # ============================================================
        # WIRE UP AUTH EVENTS
        # ============================================================

        signup_button.click(
            fn=handle_signup,
            inputs=[signup_username, signup_password, signup_confirm],
            outputs=[signup_message],
        )

        login_button.click(
            fn=handle_login,
            inputs=[login_username, login_password],
            outputs=[auth_group, app_group, logged_in_state, login_message, greeting],
        )

        logout_button.click(
            fn=handle_logout,
            outputs=[auth_group, app_group, logged_in_state, login_message, greeting],
        )

    return demo


def launch_app():
    print("=" * 60)
    print("Stock Price Prediction Analyser")
    print("=" * 60)
    print("Anyone can create their own account from the Sign Up tab.")
    print("Accounts are stored in users.json (passwords are hashed).")
    print("=" * 60)

    demo = build_interface()
    demo.launch(inbrowser=True, css=custom_css)


if __name__ == "__main__":
    launch_app()
