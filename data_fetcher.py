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
    
    # Petrol (USOIL / WTI / BRENT) Doğrudan Güncel CL=F Kontratına Bağlandı
    if clean_symbol in ["BRENT", "BRENT_PETROL", "USOIL", "PETROL", "OIL", "CL"]:
        ticker_code = "CL=F"
    elif clean_symbol in ["GRAM_ALTIN", "ALTIN", "GRAMALTIN"]:
        try:
            ons_df = yf.Ticker("GC=F").history(period="1y")
            usd_df = yf.Ticker("TRY=X").history(period="1y")
            
            if ons_df is not None and not ons_df.empty and usd_df is not None and not usd_df.empty:
                ons_df.index = pd.to_datetime(ons_df.index).tz_localize(None)
                usd_df.index = pd.to_datetime(usd_df.index).tz_localize(None)
                
                merged = pd.merge(ons_df[['Close', 'High', 'Low', 'Open']], usd_df[['Close']], left_index=True, right_index=True, suffixes=('_ons', '_usd'))
                if not merged.empty:
                    df = pd.DataFrame(index=merged.index)
                    df['Close'] = (merged['Close_ons'] * merged['Close_usd']) / 31.1035
                    df['High'] = (merged['High'] * merged['Close_usd']) / 31.1035
                    df['Low'] = (merged['Low'] * merged['Close_usd']) / 31.1035
                    df['Open'] = (merged['Open'] * merged['Close_usd']) / 31.1035
                    df = df.reset_index()
                    df.rename(columns={'index': 'Date', 'Date': 'Date'}, inplace=True)
                    return df.dropna().reset_index(drop=True)
        except Exception as e:
            print(f"Gram Altın hesaplama hatası: {e}")
        return None
    elif clean_symbol in ["ONS_ALTIN", "ONS"]:
        ticker_code = "GC=F"
    elif clean_symbol in ["GUMUS", "GRAM_GUMUS"]:
        ticker_code = "SI=F"
    elif not clean_symbol.endswith(".IS") and clean_symbol not in ["USDTRY=X", "EURTRY=X", "GC=F", "CL=F", "BZ=F", "SI=F", "^GSPC", "^IXIC"]:
        ticker_code = f"{clean_symbol}.IS"
    else:
        ticker_code = clean_symbol

    try:
        t = yf.Ticker(ticker_code)
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
        "Ham Petrol (USOil)": ("CL=F", "$") # Doğrudan en canlı US Crude Oil bağlandı
    }

    usd_price = 34.20
    try:
        usd_data = yf.Ticker("TRY=X").history(period="5d")
        if usd_data is not None and not usd_data.empty:
            usd_price = float(usd_data['Close'].iloc[-1])
    except Exception:
        pass

    for name, (ticker_code, unit) in symbols.items():
        try:
            t = yf.Ticker(ticker_code)
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
