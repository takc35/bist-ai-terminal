import pandas as pd
import yfinance as yf

def fetch_bist_ticker(ticker_symbol):
    symbol = f"{ticker_symbol.upper()}.IS" if not ticker_symbol.endswith(".IS") else ticker_symbol.upper()
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period="1y")
        if df.empty or len(df) < 50:
            return None
        df = df.reset_index()
        df = df.dropna(subset=["Close", "High", "Low", "Open"])
        df = df.rename(columns={
            "Date": "Date", "Open": "Open", "High": "High",
            "Low": "Low", "Close": "Close", "Volume": "Volume"
        })
        return df
    except Exception:
        return None
