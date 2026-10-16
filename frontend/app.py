"""
frontend/app.py
----------------
Animated Gradio frontend for Stock Price Prediction Analyser.

Authentication, stock data fetching, ML training, prediction,
and chart generation remain in the backend package.
"""

import os
import sys

# Make project root importable regardless of launch location.
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import gradio as gr

from backend.data_service import get_stock_data
from backend.ml_service import (
    train_prediction_model,
    predict_future_prices,
)
from backend.chart_service import (
    create_price_graph,
    create_prediction_graph,
)
from backend.user_store import register_user, verify_user


APP_TITLE = "Stock Price Prediction Analyser"


# ============================================================
# STOCK ANALYSIS
# ============================================================

def analyse_stock(symbol, period, future_days):
    try:
        if not symbol or not str(symbol).strip():
            return (
                "❌ Please enter a stock symbol.",
                None, None, None, None
            )

        symbol = str(symbol).strip().upper()
        future_days = max(1, min(int(future_days), 30))

        data = get_stock_data(symbol, period)

        if data is None or data.empty:
            return (
                "❌ No stock data was returned. Check the symbol.",
                None, None, None, None
            )

        if "Close" not in data.columns or len(data) < 2:
            return (
                "❌ Insufficient closing-price data for analysis.",
                None, None, None, None
            )

        historical_graph = create_price_graph(data, symbol)

        (
            model,
            X_test,
            y_test,
            predictions,
            mae,
            rmse,
            r2,
        ) = train_prediction_model(data)

        prediction_graph = create_prediction_graph(
            data, X_test, predictions, symbol
        )

        future_data = predict_future_prices(
            model, data, future_days
        )

        latest_close = float(data["Close"].iloc[-1])
        previous_close = float(data["Close"].iloc[-2])

        change = latest_close - previous_close
        change_percent = (
            change / previous_close * 100
            if previous_close != 0 else 0
        )

        highest_price = float(data["High"].max())
        lowest_price = float(data["Low"].min())
        average_price = float(data["Close"].mean())

        direction = "📈" if change >= 0 else "📉"

        summary = f"""
# 📊 Stock Analysis: {symbol}

<div class="metric-grid">
<div class="metric-card">
<div class="metric-label">Latest Close</div>
<div class="metric-value">{latest_close:,.2f}</div>
</div>
<div class="metric-card">
<div class="metric-label">Previous Close</div>
<div class="metric-value">{previous_close:,.2f}</div>
</div>
<div class="metric-card">
<div class="metric-label">Daily Change</div>
<div class="metric-value">{direction} {change:+,.2f}</div>
<div class="metric-label">{change_percent:+.2f}%</div>
</div>
<div class="metric-card">
<div class="metric-label">Period High</div>
<div class="metric-value">{highest_price:,.2f}</div>
</div>
<div class="metric-card">
<div class="metric-label">Period Low</div>
<div class="metric-value">{lowest_price:,.2f}</div>
</div>
<div class="metric-card">
<div class="metric-label">Average Close</div>
<div class="metric-value">{average_price:,.2f}</div>
</div>
</div>

---

## 🤖 Machine Learning Model

| Metric | Result |
|---|---:|
| Algorithm | Linear Regression |
| Train/Test Split | 80/20 |
| MAE | {mae:.4f} |
| RMSE | {rmse:.4f} |
| R² Score | {r2:.4f} |

> ⚠️ Predictions are estimates for educational purposes, not financial advice.
"""

        historical_table = data.tail(50).copy()

        if "Date" in historical_table.columns:
            historical_table["Date"] = (
                historical_table["Date"]
                .dt.strftime("%Y-%m-%d")
            )

        for column in ["Open", "High", "Low", "Close"]:
            if column in historical_table.columns:
                historical_table[column] = (
                    historical_table[column].round(2)
                )

        future_table = future_data.copy()

        if "Date" in future_table.columns:
            future_table["Date"] = (
                future_table["Date"]
                .dt.strftime("%Y-%m-%d")
            )

        if "Predicted Price" in future_table.columns:
            future_table["Predicted Price"] = (
                future_table["Predicted Price"].round(2)
            )

        return (
            summary,
            historical_graph,
            historical_table,
            prediction_graph,
            future_table,
        )

    except Exception as exc:
        return (
            f"❌ **Analysis failed:** {str(exc)}",
            None, None, None, None
        )


# ============================================================
# AUTHENTICATION HANDLERS
# ============================================================

def handle_signup(username, password, confirm_password):
    try:
        success, message = register_user(
            username, password, confirm_password
        )
        return message
    except Exception:
        return "❌ Account creation failed. Please try again."


def handle_login(username, password):
    try:
        success, result = verify_user(username, password)

        if success:
            display_name = str(result)

            return (
                gr.update(visible=False),
                gr.update(visible=True),
                True,
                "",
                f"## 👋 Welcome, {display_name}!",
            )

        return (
            gr.update(visible=True),
            gr.update(visible=False),
            False,
            str(result),
            "",
        )

    except Exception:
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            False,
            "❌ Login failed. Please try again.",
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
# ANIMATED CSS
# ============================================================

custom_css = r"""
/* ---------- FULL-SCREEN GLOBAL LAYOUT ---------- */
:root {
    --primary: #4f46e5;
    --primary-dark: #4338ca;
    --text-main: #172033;
    --text-muted: #64748b;
}

html, body {
    margin: 0 !important;
    padding: 0 !important;
    min-height: 100% !important;
    overflow-x: hidden !important;
    background: #e8f4ff !important;
}
body { background-attachment: fixed !important; }
.gradio-container {
    position: relative !important;
    isolation: isolate !important;
    width: 100% !important;
    max-width: none !important;
    min-height: 100vh !important;
    margin: 0 !important;
    padding: clamp(18px, 3vw, 42px) !important;
    box-sizing: border-box !important;
    background: transparent !important;
    animation: pageEnter .6s ease-out both;
}
.gradio-container > .main,
.gradio-container .main,
.gradio-container .wrap {
    max-width: none !important;
}

/* Animated full-viewport market backdrop: grid, glowing price waves and candle bars. */
.gradio-container::before {
    content: "" !important;
    position: fixed !important;
    inset: 0 !important;
    z-index: -2 !important;
    pointer-events: none !important;
    background-color: #eaf5ff !important;
    background-image:
        radial-gradient(ellipse at 12% 18%, rgba(167,139,250,.40), transparent 34%),
        radial-gradient(ellipse at 88% 22%, rgba(34,211,238,.34), transparent 35%),
        radial-gradient(ellipse at 72% 88%, rgba(96,165,250,.30), transparent 36%),
        linear-gradient(rgba(71,85,105,.065) 1px, transparent 1px),
        linear-gradient(90deg, rgba(71,85,105,.065) 1px, transparent 1px),
        linear-gradient(125deg, #f5f3ff 0%, #e0f2fe 48%, #cffafe 100%);
    background-size: auto, auto, auto, 54px 54px, 54px 54px, 220% 220% !important;
    animation: marketBackdrop 22s ease-in-out infinite alternate !important;
}
.gradio-container::after {
    content: "" !important;
    position: fixed !important;
    inset: 0 !important;
    z-index: -1 !important;
    pointer-events: none !important;
    opacity: .34 !important;
    background-image:
        linear-gradient(180deg, transparent 0 28%, rgba(16,185,129,.65) 28% 43%, transparent 43% 100%),
        linear-gradient(180deg, transparent 0 48%, rgba(239,68,68,.55) 48% 67%, transparent 67% 100%),
        linear-gradient(180deg, transparent 0 18%, rgba(16,185,129,.55) 18% 38%, transparent 38% 100%),
        linear-gradient(180deg, transparent 0 35%, rgba(239,68,68,.48) 35% 55%, transparent 55% 100%),
        linear-gradient(180deg, transparent 0 25%, rgba(16,185,129,.55) 25% 45%, transparent 45% 100%),
        linear-gradient(135deg, transparent 0 47%, rgba(79,70,229,.22) 47.2% 47.5%, transparent 47.7% 100%);
    background-size: 12px 100%, 12px 100%, 12px 100%, 12px 100%, 12px 100%, 100% 100%;
    background-position: 8% 0, 18% 0, 86% 0, 92% 0, 97% 0, 0 0;
    background-repeat: no-repeat;
    animation: candleFloat 10s ease-in-out infinite alternate;
}
@keyframes marketBackdrop {
    0% { background-position: 0 0, 0 0, 0 0, 0 0, 0 0, 0% 50%; }
    100% { background-position: 0 0, 0 0, 0 0, 26px 16px, -26px -16px, 100% 50%; }
}
@keyframes candleFloat {
    0% { transform: translateY(8px); opacity: .22; }
    100% { transform: translateY(-8px); opacity: .40; }
}
@keyframes pageEnter {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ---------- APP HEADER ---------- */
.title {
    text-align: center;
    font-size: clamp(28px, 4vw, 44px);
    line-height: 1.15;
    font-weight: 850;
    letter-spacing: -1.2px;
    color: #312e81;
    padding-top: 8px;
    animation: titleReveal .7s ease both;
}
.subtitle {
    text-align: center;
    color: #64748b;
    font-size: clamp(14px, 1.5vw, 17px);
    margin: 10px auto 28px;
}
@keyframes titleReveal {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* ---------- AUTH PAGE: FULL SCREEN, NO OUTER CARD ---------- */
.auth-shell {
    width: 100% !important;
    max-width: none !important;
    min-height: calc(100vh - 190px) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0 !important;
    margin: 0 !important;
    padding: 8px 0 28px !important;
    border: 0 !important;
    border-radius: 0 !important;
    background: transparent !important;
    box-shadow: none !important;
    backdrop-filter: none !important;
    animation: authReveal .55s ease both;
}
.auth-shell > .form,
.auth-shell > .block { min-width: 0 !important; }
@keyframes authReveal {
    from { opacity: 0; transform: translateY(14px); }
    to { opacity: 1; transform: translateY(0); }
}
.auth-welcome {
    text-align: center;
    padding: 4px 12px 20px;
}
.auth-welcome .auth-icon { font-size: 48px; line-height: 1.2; }
.auth-welcome h2 { margin: 8px 0 6px; color: #312e81; font-size: clamp(25px, 3vw, 32px); }
.auth-welcome p { margin: 0; color: #64748b; }

/* The form card is intentionally the only white panel. */
.auth-card {
    width: min(100%, 470px) !important;
    max-width: 470px !important;
    /* Move Login/Sign Up slightly lower beneath the welcome heading. */
    margin: 18px auto 30px !important;
    padding: clamp(22px, 3.5vw, 34px) !important;
    box-sizing: border-box !important;
    border: 1px solid rgba(255,255,255,.9) !important;
    border-radius: 24px !important;
    background: rgba(255,255,255,.92) !important;
    box-shadow: 0 26px 70px rgba(49,46,129,.16), 0 4px 16px rgba(15,23,42,.04) !important;
    backdrop-filter: blur(18px);
    transition: box-shadow .25s ease, transform .25s ease;
}
.auth-card > div { width: 100% !important; min-width: 0 !important; }
.auth-card:hover { box-shadow: 0 30px 80px rgba(49,46,129,.19), 0 4px 16px rgba(15,23,42,.05) !important; }

/* Force Gradio's default grey wrappers/panels to show the blue market backdrop. */
.auth-shell,
.auth-shell > div:not(.auth-card),
.auth-shell > .block,
.auth-shell .prose,
.auth-shell .markdown,
.auth-shell [data-testid="block"]:not(.auth-card) {
    background: transparent !important;
    background-color: transparent !important;
}
.auth-card .tabs,
.auth-card > div:not(.form),
.auth-card [role="tabpanel"],
.auth-card [role="tabpanel"] > div,
.auth-card [data-testid="tabitem"],
.auth-card [data-testid="tabitem"] > div,
.auth-card .tabitem,
.auth-card .tabitem > div,
.auth-card .tabitem .form,
.auth-card .tabitem .block,
.auth-card [data-testid="block"],
.auth-card .block,
.auth-card .form {
    background: transparent !important;
    background-color: transparent !important;
}
/* Preserve the clean white card and the intended tab/input/button colors. */
.auth-shell .auth-card {
    background: rgba(255,255,255,.94) !important;
}
.auth-card input,
.auth-card textarea { background: #ffffff !important; }
.auth-card [role="tablist"] { background: #f1f3ff !important; }
.auth-card [role="tablist"] > button[aria-selected="true"] { background: #ddd6fe !important; }
/* Keep Gradio's tab panel transparent: this removes the grey strip under the tabs. */
.auth-card [role="tabpanel"],
.auth-card [role="tabpanel"] > div,
.auth-card .tabitem,
.auth-card .tabitem > div,
.auth-card .tabitem .form,
.auth-card .tabitem .block {
    background: transparent !important;
    border: 0 !important;
    box-shadow: none !important;
}
.auth-card [role="tabpanel"] { overflow: visible !important; }
.auth-card [role="tablist"] {
    display: flex !important;
    width: 100% !important;
    overflow: hidden !important;
    overflow-x: hidden !important;
    white-space: normal !important;
    border: 0 !important;
    border-bottom: 0 !important;
    box-shadow: none !important;
    background: #f1f3ff !important;
    border-radius: 13px !important;
    padding: 4px !important;
    gap: 5px !important;
}
.auth-card [role="tablist"] > button {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    width: 50% !important;
    border: 0 !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    background: transparent !important;
    white-space: normal !important;
}
.auth-card [role="tablist"] > button[aria-selected="true"] {
    background: #ddd6fe !important;
    color: #3730a3 !important;
}
.auth-card [role="tablist"]::before,
.auth-card [role="tablist"]::after,
.auth-card [role="tablist"] > button::before,
.auth-card [role="tablist"] > button::after { display: none !important; content: none !important; }
.auth-card [role="tabpanel"] { padding-top: 18px !important; }
.auth-card [role="tablist"] button { font-weight: 650 !important; min-height: 42px !important; }
.auth-card input,
.auth-card textarea,
.gradio-container input,
.gradio-container textarea {
    width: 100% !important;
    box-sizing: border-box !important;
    border-radius: 12px !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}
.gradio-container input:focus,
.gradio-container textarea:focus {
    border-color: #818cf8 !important;
    box-shadow: 0 0 0 4px rgba(99,102,241,.12) !important;
}
.gradio-container label { font-weight: 600 !important; color: #334155 !important; }
.gradio-container button {
    transition: transform .2s ease, box-shadow .2s ease, background .2s ease !important;
}
.gradio-container button:hover { transform: translateY(-1px); }
.gradio-container button:active { transform: scale(.99); }
.gradio-container button.primary,
.gradio-container button[variant="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    border: 0 !important;
}
.auth-card button.primary,
.auth-card button[variant="primary"] {
    width: 100% !important;
    min-height: 50px !important;
    border-radius: 13px !important;
    font-weight: 750 !important;
    box-shadow: 0 8px 18px rgba(79,70,229,.18) !important;
}
.auth-card button[variant="primary"]:hover {
    box-shadow: 0 12px 24px rgba(79,70,229,.25) !important;
}
.auth-card .prose { color: #64748b !important; font-size: 14px !important; }
.auth-welcome .auth-kicker {
    display: inline-block;
    margin-bottom: 12px;
    padding: 6px 11px;
    border: 1px solid rgba(99,102,241,.16);
    border-radius: 999px;
    background: rgba(255,255,255,.68);
    color: #4f46e5;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1.3px;
}
.auth-footnote {
    display: block !important;
    position: static !important;
    clear: both !important;
    width: 100% !important;
    box-sizing: border-box !important;
    text-align: center !important;
    color: #64748b !important;
    font-size: 12px !important;
    line-height: 1.55 !important;
    margin: 16px auto 0 !important;
    padding: 0 4px 2px !important;
    overflow-wrap: anywhere !important;
}


/* ---------- DASHBOARD ---------- */
.dashboard-shell { animation: dashboardReveal .55s ease both; }
.dashboard-shell > .wrap { max-width: 1480px !important; margin: 0 auto !important; }
.dashboard-shell h1, .dashboard-shell h2 { letter-spacing: -.5px; }
.dashboard-shell button { border-radius: 12px !important; font-weight: 700 !important; }
.dashboard-shell input, .dashboard-shell select { min-height: 44px !important; }
@keyframes dashboardReveal {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}
.dashboard-shell > div { border-radius: 16px; }
.dashboard-shell h2, .dashboard-shell h3 { color: #312e81; }
.dashboard-shell .block { border-radius: 14px !important; }
.dashboard-shell .form, .dashboard-shell .panel { border-color: #e4e7f5 !important; }

/* ---------- STOCK METRIC CARDS ---------- */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
    margin: 20px 0;
}
.metric-card {
    background: linear-gradient(145deg, #fff, #f7f8ff);
    border: 1px solid #e6e9fb;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 5px 16px rgba(30,41,59,.035);
    transition: transform .25s ease, box-shadow .25s ease, border-color .25s ease;
}
.metric-card:hover { transform: translateY(-3px); border-color: #c7d2fe; box-shadow: 0 12px 28px rgba(79,70,229,.10); }
.metric-label { color: #64748b; font-size: 13px; margin-bottom: 8px; }
.metric-value { color: #312e81; font-size: clamp(18px, 2vw, 25px); font-weight: 800; overflow-wrap: anywhere; }
.plot-container, table, .dataframe { border-radius: 14px !important; }
.dashboard-shell .prose table { width: 100%; border-collapse: collapse; }
.dashboard-shell .prose th { background: #eef2ff; color: #3730a3; }
.dashboard-shell .prose th, .dashboard-shell .prose td { padding: 11px 14px; border-bottom: 1px solid #e8eaf5; }

/* ---------- AUTH TAB PANEL FIXES (Gradio version compatibility) ---------- */
.auth-card,
.auth-card > div,
.auth-card .tabs,
.auth-card [role="tablist"],
.auth-card [role="tabpanel"],
.auth-card [role="tabpanel"] > div,
.auth-card [data-testid="tabitem"],
.auth-card [data-testid="tabitem"] > div,
.auth-card .tabitem,
.auth-card .tabitem > div,
.auth-card .tabitem .form,
.auth-card .tabitem .block,
.auth-card [data-testid="block"] {
    box-sizing: border-box !important;
    min-width: 0 !important;
    max-width: 100% !important;
    border-color: transparent !important;
    box-shadow: none !important;
}
.auth-card .tabs,
.auth-card [role="tabpanel"],
.auth-card [role="tabpanel"] > div,
.auth-card [data-testid="tabitem"],
.auth-card [data-testid="tabitem"] > div,
.auth-card .tabitem,
.auth-card .tabitem > div,
.auth-card .tabitem .form,
.auth-card .tabitem .block,
.auth-card [data-testid="block"] {
    background: transparent !important;
}
.auth-card [role="tabpanel"] {
    height: auto !important;
    min-height: 0 !important;
    overflow: visible !important;
    padding: 18px 0 0 !important;
}
.auth-card [role="tabpanel"] > div,
.auth-card [data-testid="tabitem"] > div,
.auth-card .tabitem > div {
    height: auto !important;
    overflow: visible !important;
    padding-bottom: 0 !important;
}
.auth-card .form,
.auth-card .block,
.auth-card [data-testid="block"] {
    margin-bottom: 12px !important;
}
.auth-card button[variant="primary"] {
    display: flex !important;
    position: relative !important;
    z-index: 1 !important;
    margin-top: 8px !important;
    margin-bottom: 0 !important;
    white-space: normal !important;
    line-height: 1.35 !important;
    height: auto !important;
    min-height: 52px !important;
    padding: 12px 16px !important;
}
.auth-card .auth-footnote,
.auth-card .auth-footnote p {
    position: static !important;
    transform: none !important;
    line-height: 1.55 !important;
    white-space: normal !important;
}
.auth-card input,
.auth-card textarea {
    background: #ffffff !important;
    min-height: 48px !important;
}

@media (max-width: 700px) {
    .gradio-container { padding: 14px !important; }
    .subtitle { margin-bottom: 22px; }
    .auth-shell { min-height: calc(100vh - 150px) !important; padding-top: 0 !important; }
    .auth-card { width: 100% !important; max-width: 470px !important; margin-top: 14px !important; border-radius: 20px !important; padding: 20px !important; overflow: visible !important; }
    .auth-welcome { padding-bottom: 16px !important; }
    .auth-welcome .auth-icon { font-size: 42px !important; }
    .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
    .metric-card { padding: 14px; }
}
@media (max-width: 700px) {
    .gradio-container { padding: 14px !important; }
    .auth-card [role="tablist"] { gap: 3px !important; }
    .auth-card [role="tablist"] > button { font-size: 14px !important; padding-inline: 6px !important; }
}
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: .01ms !important; animation-iteration-count: 1 !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
"""


# ============================================================
# GRADIO INTERFACE
# ============================================================

def build_interface() -> gr.Blocks:

    with gr.Blocks(title=APP_TITLE) as demo:

        logged_in_state = gr.State(False)

        gr.Markdown(
            """
            <div class="title">
                📈 Stock Price Prediction Analyser
            </div>
            <div class="subtitle">
                Live Historical Data · Machine Learning ·
                Future Price Estimates
            </div>
            """
        )

        # ---------------- AUTHENTICATION ----------------

        with gr.Group(
            visible=True,
            elem_classes=["auth-shell"],
        ) as auth_group:

            gr.Markdown(
                """
                <div class="auth-welcome">
                    <div class="auth-kicker">YOUR MARKET WORKSPACE</div>
                    <div class="auth-icon">📈</div>
                    <h2>Welcome Back</h2>
                    <p>Sign in to explore market data and ML-powered price estimates.</p>
                </div>
                """
            )

            with gr.Group(elem_classes=["auth-card"]):
                with gr.Tabs():

                    with gr.Tab("🔓 Login"):

                        login_username = gr.Textbox(
                            label="Username",
                            placeholder="Enter your username",
                            elem_id="login-username",
                        )

                        login_password = gr.Textbox(
                            label="Password",
                            placeholder="Enter your password",
                            type="password",
                        )

                        login_button = gr.Button(
                            "🔓 Login to Dashboard",
                            variant="primary",
                            size="lg",
                        )

                        login_message = gr.Markdown("")
                        gr.Markdown("🔒 Your account details are handled by the app's authentication system.", elem_classes=["auth-footnote"])

                    with gr.Tab("✨ Sign Up"):

                        gr.Markdown(
                            "Create an account to save your access and start analysing stocks."
                        )

                        signup_username = gr.Textbox(
                            label="Choose a username",
                            placeholder="Create a username",
                        )

                        signup_password = gr.Textbox(
                            label="Choose a password",
                            placeholder="Create a strong password",
                            type="password",
                        )

                        signup_confirm = gr.Textbox(
                            label="Confirm password",
                            placeholder="Enter your password again",
                            type="password",
                        )

                        signup_button = gr.Button(
                            "✨ Create My Account",
                            variant="primary",
                            size="lg",
                        )

                        signup_message = gr.Markdown("")

        # ---------------- STOCK DASHBOARD ----------------

        with gr.Group(
            visible=False,
            elem_classes=["dashboard-shell"],
        ) as app_group:

            greeting = gr.Markdown("")

            with gr.Row():
                gr.Markdown("## 📊 Stock Analysis Dashboard")

                logout_button = gr.Button(
                    "🚪 Logout",
                    variant="secondary",
                    size="lg",
                )

            gr.Markdown(
                """
                Enter a stock ticker to analyse historical prices and
                generate a machine-learning-based estimate.

                **Examples:** `AAPL`, `MSFT`, `GOOGL`,
                `RELIANCE.NS`, `TCS.NS`, `INFY.NS`, `^NSEI`
                """
            )

            with gr.Row():

                stock_symbol = gr.Textbox(
                    label="📌 Stock Symbol",
                    placeholder="Example: RELIANCE.NS",
                    value="AAPL",
                    scale=2,
                )

                period = gr.Dropdown(
                    label="📅 Historical Period",
                    choices=[
                        "1mo", "3mo", "6mo",
                        "1y", "2y", "5y",
                    ],
                    value="1y",
                    scale=1,
                )

                future_days = gr.Slider(
                    minimum=1,
                    maximum=30,
                    value=7,
                    step=1,
                    label="🔮 Prediction Days",
                    scale=1,
                )

            analyse_button = gr.Button(
                "🔎 Analyse Stock",
                variant="primary",
                size="lg",
            )

            summary_output = gr.Markdown(
                label="Analysis Summary",
            )

            with gr.Accordion(
                "📈 Historical Price Chart",
                open=True,
            ):
                historical_graph = gr.Plot(
                    label="Historical Price",
                )

            with gr.Accordion(
                "📋 Historical Data",
                open=False,
            ):
                historical_table = gr.Dataframe(
                    label="Recent Historical Data",
                    interactive=False,
                )

            with gr.Accordion(
                "🤖 Actual vs Predicted",
                open=True,
            ):
                prediction_graph = gr.Plot(
                    label="Prediction Performance",
                )

            with gr.Accordion(
                "🔮 Future Price Prediction",
                open=True,
            ):
                future_table = gr.Dataframe(
                    label="Predicted Prices",
                    interactive=False,
                )

            gr.Markdown(
                """
                <div style="
                    text-align:center;
                    padding:20px 8px;
                    color:#64748b;
                    font-size:12px;
                ">
                    📈 Stock Price Prediction Analyser
                    <br>
                    For educational purposes only.
                    Predictions are not financial advice.
                </div>
                """
            )

            analyse_button.click(
                fn=analyse_stock,
                inputs=[
                    stock_symbol,
                    period,
                    future_days,
                ],
                outputs=[
                    summary_output,
                    historical_graph,
                    historical_table,
                    prediction_graph,
                    future_table,
                ],
            )

        # ---------------- EVENT HANDLERS ----------------

        signup_button.click(
            fn=handle_signup,
            inputs=[
                signup_username,
                signup_password,
                signup_confirm,
            ],
            outputs=[signup_message],
        )

        login_button.click(
            fn=handle_login,
            inputs=[
                login_username,
                login_password,
            ],
            outputs=[
                auth_group,
                app_group,
                logged_in_state,
                login_message,
                greeting,
            ],
        )

        logout_button.click(
            fn=handle_logout,
            outputs=[
                auth_group,
                app_group,
                logged_in_state,
                login_message,
                greeting,
            ],
        )

    return demo


# ============================================================
# LAUNCH
# ============================================================

def launch_app():
    print("=" * 60)
    print(APP_TITLE)
    print("=" * 60)
    print("Animated login and signup enabled.")
    print("Accounts are managed by backend.user_store.")
    print("=" * 60)

    demo = build_interface()

    demo.launch(
        inbrowser=True,
        css=custom_css,
    )


if __name__ == "__main__":
    launch_app() 