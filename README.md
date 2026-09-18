# Stock Price Prediction Analyser

Live stock data (Yahoo Finance) + Linear Regression prediction, with a
Gradio UI. Backend and frontend code are in separate folders. Anyone
can create their own login - there's no fixed username/password.

## Project structure

```
StockPricePrediction/
├── backend/
│   ├── data_service.py     -> fetches real live data from Yahoo Finance
│   ├── ml_service.py       -> trains the model, generates predictions
│   ├── chart_service.py    -> builds the Plotly charts
│   └── user_store.py       -> handles sign up / login, hashed passwords
├── frontend/
│   └── app.py               -> Gradio UI only, calls backend functions
├── main.py                  -> entry point, run this file
├── requirements.txt
└── users.json                -> auto-created on first sign up (not committed to git)
```

## Setup (VS Code terminal)

**1. Open the project folder in VS Code**, then open a terminal
(``Terminal > New Terminal``).

**2. Create a virtual environment:**

```
python -m venv venv
```

**3. Activate it:**

Windows (PowerShell):
```
venv\Scripts\activate
```

If PowerShell blocks it with an execution-policy error, run this once
then try activating again:
```
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Mac/Linux:
```
source venv/bin/activate
```

**4. Install dependencies:**

```
pip install --upgrade pip
pip install -r requirements.txt
```

**5. Run the app:**

```
python main.py
```

## Logging in - self sign up, no fixed credentials

The app opens on a **Login / Sign Up** screen (two tabs):

- **Sign Up tab:** anyone can create their own account - pick a
  username, a password (6+ characters), confirm it, and click
  **Create Account**.
- **Login tab:** log in with the username/password you just created.

Once logged in, the login screen is replaced with the actual stock
analyser. There's a **Logout** button to switch accounts.

Accounts are saved in `users.json` in the project folder. Passwords
are never stored as plain text - each one is hashed with
PBKDF2-HMAC-SHA256 and a unique random salt per user. This file
persists across restarts, so accounts don't disappear when you close
and reopen the app.

## Why this isn't a "demo"

- `data_service.py` calls `yfinance` directly against Yahoo Finance's
  live servers on every request. There's no cached/sample data.
- The model retrains on fresh data every time you click **Analyse
  Stock**, using whatever period you select (1mo to 5y).
- Login is a real self-serve system, not a hardcoded pair - any
  number of people can create their own accounts.
- The app runs as a real local web server on
  `http://127.0.0.1:7860` (opens in your browser automatically).
  Anyone on the same machine can open that URL, sign up, and log in.
  If you want people on a different network to reach it, you'd need
  to either deploy it to a host (Render, Hugging Face Spaces, etc.)
  or temporarily add `share=True` to `demo.launch(...)` in
  `frontend/app.py`, which gives Gradio's public tunnel link (valid
  for 72 hours).

## Notes

- Indian stocks need the `.NS` suffix, e.g. `TCS.NS`, `RELIANCE.NS`,
  `INFY.NS`. US stocks are just the ticker, e.g. `AAPL`, `MSFT`.
- The prediction model is a simple Linear Regression on day index vs
  closing price. It's meant to show a trend-based ML pipeline
  end-to-end, not to be a reliable trading signal. Good framing for a
  viva/demo: "trend-based ML estimation," not "guaranteed prediction."
