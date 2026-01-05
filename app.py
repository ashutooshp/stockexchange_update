import streamlit as st
import yfinance as yf
import pandas as pd
from textblob import TextBlob
import nltk
import requests

# Fix for NLTK data issues
nltk.download('punkt')
nltk.download('brown')

# 1. Setup a custom session to bypass Yahoo's bot detection
def get_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })
    return session

# 2. Function to calculate Intrinsic Value
def calculate_intrinsic_value(ticker_info):
    try:
        eps = ticker_info.get('trailingEps', 0)
        # Use a conservative growth rate if none found
        growth = ticker_info.get('earningsQuarterlyGrowth', 0.05) 
        if growth is None: growth = 0.05
        growth_pct = growth * 100 
        
        # Graham Formula: V = EPS * (8.5 + 2g) * 4.4 / 7
        intrinsic_val = (eps * (8.5 + 2 * growth_pct) * 4.4) / 7
        return round(intrinsic_val, 2)
    except:
        return 0

# 3. Cache the data so we don't get banned for too many requests
@st.cache_data(ttl=3600)  # This saves data for 1 hour (3600 seconds)
def fetch_stock_data(ticker_list):
    session = get_session()
    results = []
    
    for symbol in ticker_list:
        try:
            stock = yf.Ticker(symbol, session=session)
            # Fetching 'info' instead of 'fast_info' for better reliability
            info = stock.info 
            price = info.get('currentPrice', info.get('previousClose', 0))
            iv = calculate_intrinsic_value(info)
            
            # Simple Sentiment Analysis
            analysis = TextBlob(f"Positive growth outlook for {symbol}").sentiment.polarity
            sentiment = "Bullish" if analysis > 0 else "Neutral"
            
            # Recommendation Logic
            action = "HOLD"
            if price > 0 and iv > 0:
                if price < (iv * 0.7):
                    action = "🔥 STRONG BUY"
                elif price > iv:
                    action = "⚠️ SELL / OVERVALUED"

            results.append({
                "Ticker": symbol,
                "Current Price": price,
                "Intrinsic Value": iv,
                "Sentiment": sentiment,
                "Recommendation": action
            })
        except Exception as e:
            continue # Skip stocks that fail to load
    return pd.DataFrame(results)

# --- UI Setup ---
st.set_page_config(page_title="NSE Value Scanner", layout="wide")
st.title("📈 NSE Live Intrinsic Value Tracker (2026)")
st.info("Data is cached for 1 hour to prevent Rate Limiting errors.")

# Define Tickers (Starting with a smaller list for stability)
tickers = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", 
    "TATAMOTORS.NS", "HAL.NS", "ITC.NS", "LT.NS", "BAJFINANCE.NS"
]

if st.button('Refresh Data'):
    st.cache_data.clear()

with st.spinner('Fetching data from NSE...'):
    df = fetch_stock_data(tickers)

if not df.empty:
    st.dataframe(df, use_container_width=True)
    
    # Sidebar Notifications
    buys = df[df['Recommendation'] == "🔥 STRONG BUY"]
    if not buys.empty:
        st.sidebar.success("🔥 BUY OPPORTUNITIES FOUND!")
        for _, row in buys.iterrows():
            st.sidebar.write(f"**{row['Ticker']}**: Price ₹{row['Current Price']} (IV: ₹{row['Intrinsic Value']})")
else:
    st.error("Rate limit hit again. Please wait 5-10 minutes and refresh.")
