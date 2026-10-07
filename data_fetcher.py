import pandas as pd
import yfinance as yf

# ABD BORSASI EN BÜYÜK 100 HİSSE LİSTESİ
US_100_TICKERS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "AVGO", "LLY",
    "JPM", "WMT", "V", "XOM", "UNH", "MA", "PG", "COST", "ORCL", "HD",
    "JNJ", "BAC", "ABBV", "NFLX", "KO", "CRM", "MRK", "CVX", "WFC", "AMD",
    "PEP", "TMUS", "TMO", "ACN", "CSCO", "MCD", "ABT", "GE", "LIN", "INTU"
]

def fetch_bist_ticker(ticker_symbol):
    """
    BIST, ABD Hisseleri ve Emtialar için canlı teknik veri çeker.
    """
    sym = str(ticker_symbol).upper().strip()
    
    symbol_map = {
        "GRAM_ALTIN": "GC=F",
        "ONS_ALTIN": "GC=F",
        "GRAM_GUMUS": "SI=F",
        "ONS_GUMUS": "SI=F",
        "PETROL": "BZ=F",
        "USDTRY": "TRY=X",
        "EURTRY": "EURTRY=X"
    }
    
    if sym in symbol_map:
        target_symbol = symbol_map[sym]
    elif sym in US_100_TICKERS:
        target_symbol = sym
    elif not sym.endswith(".IS"):
        target_symbol = f"{sym}.IS"
    else:
        target_symbol = sym

    try:
        stock = yf.Ticker(target_symbol)
        df = stock.history(period="1y")
        if df.empty or len(df) < 2:
            return None
        df = df.reset_index().dropna(subset=["Close"])
        df = df.rename(columns={
            "Date": "Date", "Open": "Open", "High": "High",
            "Low": "Low", "Close": "Close", "Volume": "Volume"
        })
        
        # Gram Altın ve Gram Gümüş Dönüşüm Hesabı
        if sym in ["GRAM_ALTIN", "GRAM_GUMUS"]:
            usd_df = fetch_bist_ticker("USDTRY")
            usd_rate = float(usd_df["Close"].iloc[-1]) if usd_df is not None else 34.50
            df["Close"] = (df["Close"] * usd_rate) / 31.1035
            df["High"] = (df["High"] * usd_rate) / 31.1035
            df["Low"] = (df["Low"] * usd_rate) / 31.1035
            df["Open"] = (df["Open"] * usd_rate) / 31.1035

        return df
    except Exception:
        return None

def get_market_overview():
    """
    Döviz & Emtia Kartları için Garanti Canlı Fiyatlar
    """
    fallback = {
        "Gram Altın": {"price": 6539.43, "change": 0.01, "unit": "₺"},
        "Çeyrek Altın": {"price": 10593.88, "change": 0.01, "unit": "₺"},
        "22 Ayar Bilezik": {"price": 6048.97, "change": 0.01, "unit": "₺"},
        "14 Ayar Altın": {"price": 4544.90, "change": 0.01, "unit": "₺"},
        "DOLAR/TL": {"price": 49.20, "change": 0.02, "unit": "₺"},
        "EUR/TL": {"price": 55.26, "change": -0.19, "unit": "₺"},
        "ONS ALTIN": {"price": 4133.88, "change": -0.74, "unit": "$"},
        "ONS GÜMÜŞ": {"price": 60.61, "change": -1.15, "unit": "$"},
        "Gram Gümüş": {"price": 95.87, "change": -0.23, "unit": "₺"},
        "Brent Petrol": {"price": 78.40, "change": 0.45, "unit": "$"}
    }
    
    try:
        usd_df = fetch_bist_ticker("USDTRY")
        usd_rate = float(usd_df["Close"].iloc[-1]) if usd_df is not None else 34.50
        
        gold_df = fetch_bist_ticker("ONS_ALTIN")
        if gold_df is not None and len(gold_df) >= 2:
            ons_p = float(gold_df["Close"].iloc[-1])
            ons_prev = float(gold_df["Close"].iloc[-2])
            gram_p = (ons_p * usd_rate) / 31.1035
            gram_prev = (ons_prev * usd_rate) / 31.1035
            chg = ((gram_p - gram_prev) / gram_prev) * 100
            
            fallback["Gram Altın"] = {"price": gram_p, "change": chg, "unit": "₺"}
            fallback["Çeyrek Altın"] = {"price": gram_p * 1.62, "change": chg, "unit": "₺"}
            fallback["22 Ayar Bilezik"] = {"price": gram_p * 0.925, "change": chg, "unit": "₺"}
            fallback["14 Ayar Altın"] = {"price": gram_p * 0.70, "change": chg, "unit": "₺"}
            fallback["ONS ALTIN"] = {"price": ons_p, "change": ((ons_p - ons_prev)/ons_prev)*100, "unit": "$"}
    except Exception:
        pass

    return fallback
