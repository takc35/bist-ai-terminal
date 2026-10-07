import pandas as pd
import yfinance as yf

def fetch_bist_ticker(ticker_symbol):
    """
    BIST, ABD hisseleri, Kripto ve Emtialar için canlı veri çeker.
    """
    sym = ticker_symbol.upper().strip()
    
    # Özel Sembol Eşleştirmeleri
    symbol_map = {
        "ONS_ALTIN": "GC=F",
        "ONS_GUMUS": "SI=F",
        "PETROL": "BZ=F",
        "USDTRY": "USDTRY=X",
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
        df = stock.history(period="1y")
        if df.empty or len(df) < 5:
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

def get_market_overview():
    """
    Emtia, Döviz, ABD Hisseleri ve Fonlar için anlık canlı fiyat verilerini hazırlar.
    """
    items = {
        "Gram Altın": {"symbol": "GC=F", "is_gram_gold": True},
        "Ons Altın": {"symbol": "GC=F", "unit": "$"},
        "Gram Gümüş": {"symbol": "SI=F", "is_gram_silver": True},
        "Ons Gümüş": {"symbol": "SI=F", "unit": "$"},
        "Brent Petrol": {"symbol": "BZ=F", "unit": "$"},
        "USD/TRY": {"symbol": "USDTRY=X", "unit": "₺"},
        "EUR/TRY": {"symbol": "EURTRY=X", "unit": "₺"},
        "NVDA": {"symbol": "NVDA", "unit": "$"},
        "AAPL": {"symbol": "AAPL", "unit": "$"},
        "TSLA": {"symbol": "TSLA", "unit": "$"},
        "BTC/USDT": {"symbol": "BTC-USD", "unit": "$"},
        "ETH/USDT": {"symbol": "ETH-USD", "unit": "$"}
    }
    
    # USDTRY Kurunu al (Gram Altın ve Gram Gümüş hesabı için)
    usd_df = fetch_bist_ticker("USDTRY")
    usd_rate = float(usd_df["Close"].iloc[-1]) if usd_df is not None else 34.0
    
    results = {}
    for name, meta in items.items():
        df = fetch_bist_ticker(meta["symbol"])
        if df is not None and len(df) >= 2:
            last_p = float(df["Close"].iloc[-1])
            prev_p = float(df["Close"].iloc[-2])
            
            # Gram Altın Hesabı: (Ons Fiyatı * Dolar Kuru) / 31.1035
            if meta.get("is_gram_gold"):
                last_p = (last_p * usd_rate) / 31.1035
                prev_p = (float(df["Close"].iloc[-2]) * usd_rate) / 31.1035
                unit = "₺"
            # Gram Gümüş Hesabı: (Ons Gümüş * Dolar Kuru) / 31.1035
            elif meta.get("is_gram_silver"):
                last_p = (last_p * usd_rate) / 31.1035
                prev_p = (float(df["Close"].iloc[-2]) * usd_rate) / 31.1035
                unit = "₺"
            else:
                unit = meta.get("unit", "")

            chg = ((last_p - prev_p) / prev_p) * 100
            results[name] = {"price": last_p, "change": chg, "unit": unit}
            
    return results
