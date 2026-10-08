import yfinance as yf
import pandas as pd

BIST_30_TICKERS = [
    "AKBNK", "ALARK", "ASELS", "BIMAS", "EKGYO", "ENJSA", "EREGL", "FROTO", 
    "GARAN", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KRDMD", "MGROS", 
    "ODAS", "OYAKC", "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TCELL", 
    "THYAO", "TOASO", "TUPRS", "VAKBN", "YKBNK"
]

US_100_TICKERS = [
    "AAPL", "MSFT", "AMZN", "NVDA", "GOOGL", "META", "TSLA", "AVGO", "COST", "PEP"
]

def fetch_bist_ticker(symbol):
    if not symbol:
        return None
    clean_symbol = symbol.strip().upper()
    
    # Brent Petrol & Emtia Takma Adları
    if clean_symbol in ["BRENT", "BRENT_PETROL"]:
        ticker_code = "BZ=F"
    elif clean_symbol in ["ONS_ALTIN"]:
        ticker_code = "GC=F"
    elif clean_symbol in ["GRAM_ALTIN", "ALTIN"]:
        try:
            ons = yf.Ticker("GC=F").history(period="5d")
            usd = yf.Ticker("TRY=X").history(period="5d")
            if not ons.empty and not usd.empty:
                df = pd.DataFrame()
                df['Close'] = (ons['Close'] * usd['Close']) / 31.1035
                df['High'] = (ons['High'] * usd['High']) / 31.1035
                df['Low'] = (ons['Low'] * usd['Low']) / 31.1035
                df['Open'] = (ons['Open'] * usd['Open']) / 31.1035
                df['Date'] = df.index
                return df.dropna().reset_index(drop=True)
        except Exception:
            pass
        return None
    elif not clean_symbol.endswith(".IS") and clean_symbol not in ["USDTRY=X", "EURTRY=X", "GC=F", "CL=F", "BZ=F", "SI=F", "^GSPC", "^IXIC"]:
        ticker_code = f"{clean_symbol}.IS"
    else:
        ticker_code = clean_symbol

    try:
        t = yf.Ticker(ticker_code)
        df = t.history(period="1y")
        
        # Brent Petrol vadeli kontrat geçişlerinde boş dönerse WTI (CL=F) dene
        if (df is None or df.empty) and ticker_code == "BZ=F":
            t = yf.Ticker("CL=F")
            df = t.history(period="1y")

        if (df is None or df.empty) and ticker_code.endswith(".IS"):
            t = yf.Ticker(clean_symbol)
            df = t.history(period="1y")
            
        if df is not None and not df.empty:
            df = df.reset_index()
            return df
    except Exception as e:
        print(f"Veri çekme hatası ({symbol}): {e}")
        
    return None

def get_market_overview():
    overview = {}
    symbols = {
        "Dolar / TL": ("TRY=X", "₺"),
        "Euro / TL": ("EURTRY=X", "₺"),
        "Gram Altın": ("GC=F", "₺"),
        "Ons Altın": ("GC=F", "$"),
        "Gram Gümüş": ("SI=F", "₺"),
        "Brent Petrol": ("BZ=F", "$")
    }

    usd_price = 34.20
    try:
        usd_data = yf.Ticker("TRY=X").history(period="5d")
        if not usd_data.empty:
            usd_price = float(usd_data['Close'].iloc[-1])
    except Exception:
        pass

    for name, (ticker_code, unit) in symbols.items():
        try:
            t = yf.Ticker(ticker_code)
            df = t.history(period="5d")
            
            if (df is None or df.empty or len(df) < 2) and ticker_code == "BZ=F":
                t = yf.Ticker("CL=F")
                df = t.history(period="5d")

            if df is not None and not df.empty and len(df) >= 2:
                last_p = float(df['Close'].iloc[-1])
                prev_p = float(df['Close'].iloc[-2])
                
                if name == "Gram Altın" or name == "Gram Gümüş":
                    last_p = (last_p * usd_price) / 31.1035
                    prev_p = (prev_p * usd_price) / 31.1035

                chg = ((last_p - prev_p) / prev_p) * 100 if prev_p != 0 else 0.0
                overview[name] = {"price": last_p, "change": chg, "unit": unit}
            else:
                overview[name] = {"price": 0.0, "change": 0.0, "unit": unit}
        except Exception:
            overview[name] = {"price": 0.0, "change": 0.0, "unit": unit}

    return overview
