import pandas as pd
import yfinance as yf

# ABD BORSASI EN BÜYÜK 100 HİSSE LİSTESİ
US_100_TICKERS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "AVGO", "LLY",
    "JPM", "WMT", "V", "XOM", "UNH", "MA", "PG", "COST", "ORCL", "HD",
    "JNJ", "BAC", "ABBV", "NFLX", "KO", "CRM", "MRK", "CVX", "WFC", "AMD",
    "PEP", "TMUS", "TMO", "ACN", "CSCO", "MCD", "ABT", "GE", "LIN", "INTU",
    "TXN", "DHR", "DIS", "PM", "AXP", "QCOM", "NOW", "VZ", "AMAT", "IBM",
    "AMGN", "CAT", "LOW", "BKNG", "PFE", "UBER", "GS", "UNP", "SPGI", "HON",
    "COP", "RTX", "LMT", "SBUX", "SYK", "T", "PLTR", "BLK", "BA", "DE", "ADI",
    "MDLZ", "ISRG", "TJX", "VRTX", "PGR", "MMC", "GILD", "REGN", "LRCX", "SCHW",
    "ADP", "PANW", "CI", "C", "MU", "EOG", "LRCX", "SLB", "AON", "MO", "FI",
    "WM", "BMY", "GEV", "NKE", "SO", "ITW", "SHW", "CL", "TGT", "BDX", "BSX"
]

def fetch_bist_ticker(ticker_symbol):
    """
    BIST, ABD Hisseleri ve Emtialar için canlı veri çeker.
    """
    sym = str(ticker_symbol).upper().strip()
    
    symbol_map = {
        "ONS_ALTIN": "GC=F",
        "ONS_GUMUS": "SI=F",
        "PETROL": "BZ=F",
        "USDTRY": "USDTRY=X",
        "EURTRY": "EURTRY=X"
    }
    
    if sym in symbol_map:
        target_symbol = symbol_map[sym]
    elif sym in US_100_TICKERS or sym.replace("-", ".") in US_100_TICKERS:
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
        df = df.reset_index()
        df = df.dropna(subset=["Close"])
        df = df.rename(columns={
            "Date": "Date", "Open": "Open", "High": "High",
            "Low": "Low", "Close": "Close", "Volume": "Volume"
        })
        return df
    except Exception:
        return None

def get_market_overview():
    """
    Döviz ve Emtialar için canlı fiyat listesi.
    """
    items = {
        "USD/TRY": {"symbol": "USDTRY=X", "unit": "₺"},
        "EUR/TRY": {"symbol": "EURTRY=X", "unit": "₺"},
        "Ons Altın": {"symbol": "GC=F", "unit": "$"},
        "Ons Gümüş": {"symbol": "SI=F", "unit": "$"},
        "Brent Petrol": {"symbol": "BZ=F", "unit": "$"},
        "Gram Altın": {"symbol": "GC=F", "is_gram_gold": True, "unit": "₺"},
        "Gram Gümüş": {"symbol": "SI=F", "is_gram_silver": True, "unit": "₺"}
    }
    
    usd_rate = 34.50
    try:
        usd_df = fetch_bist_ticker("USDTRY")
        if usd_df is not None and not usd_df.empty:
            usd_rate = float(usd_df["Close"].iloc[-1])
    except Exception:
        pass
    
    results = {}
    for name, meta in items.items():
        try:
            df = fetch_bist_ticker(meta["symbol"])
            if df is not None and len(df) >= 2:
                last_p = float(df["Close"].iloc[-1])
                prev_p = float(df["Close"].iloc[-2])
                
                if meta.get("is_gram_gold"):
                    last_p = (last_p * usd_rate) / 31.1035
                    prev_p = (prev_p * usd_rate) / 31.1035
                elif meta.get("is_gram_silver"):
                    last_p = (last_p * usd_rate) / 31.1035
                    prev_p = (prev_p * usd_rate) / 31.1035

                chg = ((last_p - prev_p) / prev_p) * 100 if prev_p != 0 else 0.0
                results[name] = {"price": last_p, "change": chg, "unit": meta["unit"]}
        except Exception:
            continue
            
    return results
