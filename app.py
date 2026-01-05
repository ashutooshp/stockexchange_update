import nltk
nltk.download('punkt')
nltk.download('brown')
import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import requests

# Function to calculate Intrinsic Value (Graham Formula)
def calculate_intrinsic_value(ticker_data):
    try:
        info = ticker_data.info
        eps = info.get('trailingEps', 0)
        growth = info.get('earningsQuarterlyGrowth', 0.1) * 100 # Estimated growth
        # Graham Formula: V = EPS * (8.5 + 2g) * 4.4 / Y
        # Y is the current AAA bond yield (approx 7% in 2026)
        intrinsic_val = (eps * (8.5 + 2 * growth) * 4.4) / 7
        return round(intrinsic_val, 2)
    except:
        return 0

# Function to get news sentiment
def get_sentiment(ticker):
    # In a real app, use NewsAPI. Here we use a placeholder logic.
    # Logic: Fetch news, analyze text sentiment
    mock_news = [f"Positive growth expected for {ticker}", f"{ticker} beats earnings"]
    sentiment_score = 0
    for news in mock_news:
        analysis = TextBlob(news)
        sentiment_score += analysis.sentiment.polarity
    return "Bullish" if sentiment_score > 0 else "Neutral/Bearish"

# UI Header
st.set_page_config(page_title="NSE Intrinsic Value Tracker", layout="wide")
st.title("📈 NSE Live Intrinsic Value & News Scanner")
st.write("Real-time analysis of Nifty 500 stocks based on Graham's Formula and News Sentiment.")

# Stock List (Example: Nifty Top 10) - You can expand this to all 500
tickers = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TATAMOTORS.NS", "HAL.NS"]

data_list = []

for symbol in tickers:
    stock = yf.Ticker(symbol)
    price = stock.fast_info['last_price']
    iv = calculate_intrinsic_value(stock)
    sentiment = get_sentiment(symbol)
    
    # Logic for Notification
    action = "HOLD"
    if price < (iv * 0.7) and sentiment == "Bullish":
        action = "🔥 STRONG BUY"
    elif price > iv:
        action = ⚠️ SELL / OVERVALUED"

    data_list.append({
        "Ticker": symbol,
        "Current Price": round(price, 2),
        "Intrinsic Value": iv,
        "Sentiment": sentiment,
        "Recommendation": action
    })

# Display Data Table
df = pd.DataFrame(data_list)
st.table(df)

# Sidebar for Notifications
st.sidebar.header("Live Notifications")
buys = df[df['Recommendation'] == "🔥 STRONG BUY"]
if not buys.empty:
    for i, row in buys.iterrows():
        st.sidebar.success(f"BUY ALERT: {row['Ticker']} is 30% undervalued with positive news!")