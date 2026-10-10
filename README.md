# 📈 Stock Price Prediction Analyser

> An end-to-end Python application for real-time stock data analysis and trend-based price estimation using Python, Machine Learning, Yahoo Finance, Plotly, and Gradio.

A modular ML-powered application that fetches historical stock market data, processes it, trains a Linear Regression model, generates trend-based estimations, and presents interactive visualizations through a Gradio web interface.

The project also includes a self-service authentication system with password hashing and a modular frontend/backend architecture.

## ✨ Project Highlights

- 📊 Real market data using Yahoo Finance
- 🤖 Machine Learning with Linear Regression
- 📈 Interactive Plotly charts
- 🖥️ Gradio-based web interface
- 🔐 User Sign Up & Login
- 🔑 PBKDF2-HMAC-SHA256 password hashing
- 🧩 Modular backend architecture
- 🌐 Support for Indian and US stock tickers
- 🐍 Built with Python

The **Stock Price Prediction Analyser** is a modular Python application that fetches historical stock market data from Yahoo Finance, processes the data, trains a Linear Regression model, generates trend-based estimations, and presents the results through an interactive Gradio interface.

The project also includes a self-service user authentication system with password hashing and separate frontend/backend modules.

---

## 🚀 Key Features

- 📊 Fetch stock market data from Yahoo Finance
- 🤖 Machine Learning-based trend estimation
- 📈 Linear Regression model
- 📉 Interactive Plotly visualizations
- 🖥️ Interactive Gradio web interface
- 🔐 User Sign Up and Login system
- 🔑 Password hashing using PBKDF2-HMAC-SHA256
- 👤 Multiple user accounts
- 🔄 Model training using freshly retrieved historical data
- 🇮🇳 Support for Indian stock tickers
- 🌎 Support for US stock tickers
- 🧩 Modular backend architecture
- 🔗 Separate frontend and backend components

---

## 🧠 How the Application Works

```text
                    USER
                      │
                      ▼
             ┌─────────────────┐
             │  Gradio UI      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Authentication  │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Stock Ticker    │
             │ + Time Period   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Yahoo Finance   │
             │ Data Fetching   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Data Processing │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Linear          │
             │ Regression      │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Trend Estimation│
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │ Plotly Charts   │
             └─────────────────┘
## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| Language | Python |
| Machine Learning | Scikit-learn, Linear Regression |
| Data Processing | Pandas, NumPy |
| Financial Data | yfinance / Yahoo Finance |
| Visualization | Plotly |
| UI | Gradio |
| Authentication | PBKDF2-HMAC-SHA256, Random Salt |
| Storage | JSON |
| Development | VS Code, Git, GitHub |

📂 Project Structure
StockPricePrediction/
│
├── backend/
│   │
│   ├── data_service.py
│   │   └── Fetches stock data from Yahoo Finance
│   │
│   ├── ml_service.py
│   │   └── Handles model training and predictions
│   │
│   ├── chart_service.py
│   │   └── Generates Plotly visualizations
│   │
│   └── user_store.py
│       └── Handles user registration and authentication
│
├── frontend/
│   │
│   └── app.py
│       └── Gradio user interface
│
├── main.py
│   └── Application entry point
│
├── requirements.txt
└── .gitignore
🔐 Authentication System

The application provides a self-service authentication system.

Sign Up

Users can create their own account using:

Username
Password
Password confirmation
Login

Registered users can log in using their credentials.

Password Security

Passwords are not stored as plain text.

The application uses:

PBKDF2-HMAC-SHA256
        +
Unique Random Salt

for password hashing.

User account information is stored locally in:

users.json

users.json should remain excluded from the public Git repository because it may contain user account information.

📊 Stock Analysis Workflow

The application follows the workflow below:

1. User Login / Sign Up
          ↓
2. Enter Stock Ticker
          ↓
3. Select Historical Period
          ↓
4. Fetch Data from Yahoo Finance
          ↓
5. Process Historical Data
          ↓
6. Prepare Features
          ↓
7. Train Linear Regression Model
          ↓
8. Generate Trend-Based Estimation
          ↓
9. Create Interactive Charts
          ↓
10. Display Results
🤖 Machine Learning Approach

The current version uses Linear Regression to estimate the trend of stock closing prices.

The basic relationship used by the model is:

Day Index  →  Closing Price

The machine learning pipeline follows:

Data Collection
      ↓
Data Preprocessing
      ↓
Feature Preparation
      ↓
Model Training
      ↓
Prediction
      ↓
Visualization

The purpose of the model is to demonstrate an end-to-end machine learning workflow using real market data.

📈 Supported Stock Tickers
🇮🇳 Indian Stocks

Indian stocks generally use the .NS suffix.

Examples:

TCS.NS
RELIANCE.NS
INFY.NS
HDFCBANK.NS
ICICIBANK.NS
🇺🇸 US Stocks

Examples:

AAPL
MSFT
GOOGL
AMZN
TSLA
⚙️ Installation & Setup
1. Clone the Repository
```bash
git clone https://github.com/Princekumar9027/Stock-Price-Prediction-Analyser.git
```
Move into the project directory:
cd Stock-Price-Prediction-Analyser

2. Create a Virtual Environment
python -m venv venv

4. Activate the Virtual Environment
Windows PowerShell
venv\Scripts\activate

If PowerShell blocks script execution, run:

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Then activate the environment again:

venv\Scripts\activate
macOS / Linux
source venv/bin/activate
4. Install Dependencies

Upgrade pip:

python -m pip install --upgrade pip

Install project dependencies:

pip install -r requirements.txt
5. Run the Application

Run:

python main.py

The Gradio application will start locally.

The application can be accessed through the local Gradio interface.

🖥️ Application Screenshots
🔐 Login / Sign Up

Add your application login screenshot here.

📊 Stock Analysis Dashboard

Add your stock analysis dashboard screenshot here.

📈 Prediction / Visualization

Add your Plotly chart screenshot here.

Screenshots will be added to this README to demonstrate the application's user interface and functionality.

📌 Important Project Highlights
Real Market Data

The application retrieves stock data through yfinance instead of relying on manually hardcoded sample datasets.

Modular Architecture

The project separates major responsibilities into backend services:

Data fetching
Machine Learning
Chart generation
Authentication
User Authentication

Users can create their own accounts instead of using a fixed username and password.

Interactive Interface

The Gradio interface allows users to interact with the application without directly working with Python code.

Machine Learning Pipeline

The project demonstrates a complete basic ML workflow:

Data → Processing → Training → Prediction → Visualization
🎯 Learning Outcomes

Through this project, I gained practical experience in:

Python application development
Machine Learning workflows
Linear Regression
Data preprocessing
Financial data retrieval
Data visualization
Interactive UI development
Gradio
Plotly
Authentication systems
Password hashing
Modular software architecture
Frontend/backend separation
Git and GitHub
Virtual environments
Dependency management
🔒 Security

The following files should not be committed to the public repository:

users.json
.env
*.db
venv/
.venv/
__pycache__/
*.pyc

Recommended .gitignore:

venv/
.venv/
__pycache__/
*.pyc
users.json
.env
*.db
⚠️ Limitations

The current version uses a simple Linear Regression model based on historical closing-price trends.

It does not account for all factors that can affect financial markets, such as:

Market sentiment
News
Economic conditions
Company fundamentals
Technical indicators
Unexpected market events

Therefore, the generated result should be considered a trend-based ML estimation, not a guaranteed future stock price.

🔮 Future Improvements

Possible future improvements include:

📊 Additional technical indicators
🤖 Advanced Machine Learning models
🧠 Deep Learning-based forecasting
📈 Better model evaluation
📉 Historical prediction performance analysis
🔐 Database-backed authentication
☁️ Cloud deployment
🌐 Production-ready backend API
📱 Improved responsive interface
📊 Additional market analytics
🎓 Project Purpose

This project was developed as a practical implementation of:

Python
   +
Data Processing
   +
Machine Learning
   +
Financial Data
   +
Visualization
   +
Web Interface
   +
Authentication

The goal is to demonstrate how different software and machine learning components can be integrated into a single working application.

👨‍💻 Author
Prince Kumar Singh

MCA (Artificial Intelligence) Student

Interested in:

Software Development
Full Stack Development
Python Development
Artificial Intelligence
Machine Learning
Backend Development
Data-driven Applications
🔗 Connect With Me

GitHub:
https://github.com/Princekumar9027

LinkedIn:
https://www.linkedin.com/in/prince-kumar-singh-a5a969306/

⭐ Support

If you find this project interesting, feel free to explore the repository and share feedback.

Learn → Build → Debug → Improve → Repeat 🚀

⚠️ Disclaimer

This project is developed for educational and software-development purposes.

The output generated by the application represents model-based trend estimation and should not be considered financial advice, investment advice, or a guaranteed prediction of future stock prices.
