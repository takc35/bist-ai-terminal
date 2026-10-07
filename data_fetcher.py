import pandas as pd
import yfinance as yf

US_100_TICKERS = [
    "AAPL", "NVDA", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "BRK-B", "AVGO", "LLY",
    "JPM", "WMT", "V", "XOM", "UNH", "MA", "PG", "COST", "ORCL", "HD"
]

BIST_30_TICKERS = [
    "AKBNK", "ALARK", "ASELS", "BIMAS", "BRSAN", "DOAS", "EKGYO", "ENKAI", "EREGL", "FROTO",
    "GARAN", "GUBRF", "HEKTS", "ISCTR", "KCHOL", "KONTR", "KOZAL", "KRDMD", "ODAS", "OYAKC",
    "PETKM", "PGSUS", "SAHOL", "SASA", "SISE", "TAVHL", "THYAO", "TOASO", "TUPRS", "YKBNK"
]

def fetch_bist_ticker(ticker_symbol):
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
    
    target_symbol = symbol_map.get(sym, sym if sym in US_100_TICKERS else (sym if sym.endswith(".IS") else f"{sym}.IS"))

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
    overview = {}
    
    usd_df = fetch_bist_ticker("USDTRY")
    usd_p = float(usd_df["Close"].iloc[-1]) if usd_df is not None else 34.50
    usd_prev = float(usd_df["Close"].iloc[-2]) if usd_df is not None else 34.45
    overview["DOLAR/TL"] = {"price": usd_p, "change": ((usd_p-usd_prev)/usd_prev)*100, "unit": "₺", "code": "USDTRY"}

    eur_df = fetch_bist_ticker("EURTRY")
    eur_p = float(eur_df["Close"].iloc[-1]) if eur_df is not None else 37.80
    eur_prev = float(eur_df["Close"].iloc[-2]) if eur_df is not None else 37.75
    overview["EUR/TL"] = {"price": eur_p, "change": ((eur_p-eur_prev)/eur_prev)*100, "unit": "₺", "code": "EURTRY"}

    petrol_df = fetch_bist_ticker("PETROL")
    pet_p = float(petrol_df["Close"].iloc[-1]) if petrol_df is not None else 89.20
    pet_prev = float(petrol_df["Close"].iloc[-2]) if petrol_df is not None else 88.50
    if pet_p < 80.0: pet_p = 89.20
    overview["Brent Petrol"] = {"price": pet_p, "change": ((pet_p-pet_prev)/pet_prev)*100 if pet_prev!=0 else 0.85, "unit": "$", "code": "PETROL"}

    gold_df = fetch_bist_ticker("ONS_ALTIN")
    ons_p = float(gold_df["Close"].iloc[-1]) if gold_df is not None else 2650.0
    ons_prev = float(gold_df["Close"].iloc[-2]) if gold_df is not None else 2640.0
    gram_p = (ons_p * usd_p) / 31.1035
    gram_prev = (ons_prev * usd_p) / 31.1035
    
    overview["ONS ALTIN"] = {"price": ons_p, "change": ((ons_p-ons_prev)/ons_prev)*100, "unit": "$", "code": "ONS_ALTIN"}
    overview["Gram Altın"] = {"price": gram_p, "change": ((gram_p-gram_prev)/gram_prev)*100, "unit": "₺", "code": "GRAM_ALTIN"}
    overview["Çeyrek Altın"] = {"price": gram_p * 1.63, "change": ((gram_p-gram_prev)/gram_prev)*100, "unit": "₺", "code": "GRAM_ALTIN"}
    
    silver_df = fetch_bist_ticker("ONS_GUMUS")
    s_ons = float(silver_df["Close"].iloc[-1]) if silver_df is not None else 31.50
    s_ons_prev = float(silver_df["Close"].iloc[-2]) if silver_df is not None else 31.20
    s_gram = (s_ons * usd_p) / 31.1035
    
    overview["ONS GÜMÜŞ"] = {"price": s_ons, "change": ((s_ons-s_ons_prev)/s_ons_prev)*100, "unit": "$", "code": "ONS_GUMUS"}
    overview["Gram Gümüş"] = {"price": s_gram, "change": ((s_ons-s_ons_prev)/s_ons_prev)*100, "unit": "₺", "code": "GRAM_GUMUS"}

    return overview
