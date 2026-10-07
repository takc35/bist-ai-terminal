import pandas as pd
import yfinance as yf

def fetch_bist_ticker(ticker_symbol):
    """
    BIST, ABD Hisseleri, Kripto ve Emtialar için güvenli canlı veri çeker.
    """
    sym = str(ticker_symbol).upper().strip()
    
    symbol_map = {
        "ONS_ALTIN": "GC=F",
        "ONS_GUMUS": "SI=F",
        "PETROL": "BZ=F",
        "USDTRY": "TRY=X",
        "EURTRY": "EURTRY=X",
        "BTCUSDT": "BTC-USD",
        "ETHUSDT": "ETH-USD"
    }
    
    if sym in symbol_map:
        target_symbol = symbol_map[sym]
    elif sym in ["NVDA", "AAPL", "TSLA", "MSFT", "AMZN", "GOOGL", "META"]:
        target_symbol = sym
    elif not sym.endswith(".IS"):
        target_symbol = f"{sym}.IS"
    else:
        target_symbol = sym

    try:
        stock = yf.Ticker(target_symbol)
        df = stock.history(period="5d")
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
    Döviz, Emtia ve ABD Hisseleri için hata korumalı canlı veri listesi üretir.
    """
    items = {
        "USD/TRY": {"symbol": "TRY=X", "unit": "₺"},
        "EUR/TRY": {"symbol": "EURTRY=X", "unit": "₺"},
        "Ons Altın": {"symbol": "GC=F", "unit": "$"},
        "Ons Gümüş": {"symbol": "SI=F", "unit": "$"},
        "Brent Petrol": {"symbol": "BZ=F", "unit": "$"},
        "Gram Altın": {"symbol": "GC=F", "is_gram_gold": True, "unit": "₺"},
        "Gram Gümüş": {"symbol": "SI=F", "is_gram_silver": True, "unit": "₺"},
        "NVDA": {"symbol": "NVDA", "unit": "$"},
        "AAPL": {"symbol": "AAPL", "unit": "$"},
        "TSLA": {"symbol": "TSLA", "unit": "$"},
        "BTC/USDT": {"symbol": "BTC-USD", "unit": "$"},
        "ETH/USDT": {"symbol": "ETH-USD", "unit": "$"}
    }
    
    # Varsayılan USD Kuru (Veri alınamazsa fallback olarak kullanılır)
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
