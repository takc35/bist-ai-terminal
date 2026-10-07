import numpy as np
import pandas as pd

def sma(s, n):
    return s.rolling(n).mean()

def ema(s, n):
    return s.ewm(span=n, adjust=False).mean()

def rsi(close, n=14):
    d = close.diff()
    gain = d.clip(lower=0)
    loss = -d.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/n, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/n, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def macd(close):
    fast = ema(close, 12)
    slow = ema(close, 26)
    line = fast - slow
    signal = ema(line, 9)
    return line, signal, line - signal

def atr(df, n=14):
    prev = df["Close"].shift(1)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - prev).abs(),
        (df["Low"] - prev).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(n).mean()

def add_indicators(df):
    df = df.copy()
    c = df["Close"]
    for n in [5, 10, 20, 25, 50, 100, 200]:
        df[f"SMA{n}"] = sma(c, n)
    df["RSI14"] = rsi(c)
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = macd(c)
    df["ATR14"] = atr(df)
    df["VOL20"] = df["Volume"].rolling(20).mean() if "Volume" in df else 1.0
    df["VOL_RATIO"] = df["Volume"] / df["VOL20"] if "Volume" in df else 1.0
    df["ROC20"] = c.pct_change(20) * 100
    df["ROC60"] = c.pct_change(60) * 100
    df = df.bfill().ffill()
    return df

def support_resistance(df, window=20):
    try:
        x = df.tail(120)
        sup_series = x["Low"].rolling(window, min_periods=1).min().dropna()
        res_series = x["High"].rolling(window, min_periods=1).max().dropna()
        
        support = float(sup_series.iloc[-1]) if not sup_series.empty else float(df["Close"].iloc[-1] * 0.95)
        resistance = float(res_series.iloc[-1]) if not res_series.empty else float(df["Close"].iloc[-1] * 1.05)
        return support, resistance
    except Exception:
        last_c = float(df["Close"].iloc[-1])
        return last_c * 0.95, last_c * 1.05

def technical_score(df):
    x = df.iloc[-1]
    score = 50.0
    if pd.notna(x.get("SMA200")) and x["Close"] > x["SMA200"]: score += 15
    else: score -= 15
    if pd.notna(x.get("SMA50")) and x["Close"] > x["SMA50"]: score += 8
    else: score -= 8
    if pd.notna(x.get("SMA25")) and x["Close"] > x["SMA25"]: score += 5
    else: score -= 5

    rsi_val = x.get("RSI14", 50)
    if 50 <= rsi_val <= 68: score += 7
    elif rsi_val < 30: score += 3
    elif rsi_val > 75: score -= 7

    if x.get("MACD", 0) > x.get("MACD_SIGNAL", 0): score += 7
    else: score -= 4

    vol_r = x.get("VOL_RATIO", 1)
    if vol_r >= 1.5: score += 5
    elif vol_r < 0.7: score -= 2

    return round(float(np.clip(score, 0, 100)), 1)

def momentum_score(df):
    x = df.iloc[-1]
    score = 50.0
    roc20 = x.get("ROC20", 0)
    roc60 = x.get("ROC60", 0)
    if pd.notna(roc20): score += np.clip(roc20, -20, 20) * 0.7
    if pd.notna(roc60): score += np.clip(roc60, -30, 30) * 0.35
    if x.get("MACD", 0) > x.get("MACD_SIGNAL", 0): score += 7
    if pd.notna(x.get("SMA25")) and x["Close"] > x["SMA25"]: score += 5
    return round(float(np.clip(score, 0, 100)), 1)

def trend_score(df):
    x = df.iloc[-1]
    mas = [x.get("SMA25"), x.get("SMA50"), x.get("SMA100"), x.get("SMA200")]
    valid = [v for v in mas if pd.notna(v)]
    if not valid: return 50.0
    above = sum(x["Close"] > v for v in valid)
    slope_bonus = 5 if pd.notna(x.get("SMA50")) and len(df) >= 10 and x["SMA50"] > df["SMA50"].iloc[-10] else -5
    return round(float(np.clip(25 + 15*above + slope_bonus, 0, 100)), 1)

def crossover_flags(df):
    out = {}
    for a, b, name in [(25, 50, "25_50"), (50, 200, "50_200")]:
        A = df[f"SMA{a}"] if f"SMA{a}" in df else pd.Series()
        B = df[f"SMA{b}"] if f"SMA{b}" in df else pd.Series()
        if len(A) >= 2 and len(B) >= 2 and pd.notna(A.iloc[-1]) and pd.notna(B.iloc[-1]):
            out[name+"_golden"] = bool(A.iloc[-1] > B.iloc[-1] and A.iloc[-2] <= B.iloc[-2])
            out[name+"_death"] = bool(A.iloc[-1] < B.iloc[-1] and A.iloc[-2] >= B.iloc[-2])
        else:
            out[name+"_golden"] = False
            out[name+"_death"] = False
            
    last_c = df["Close"].iloc[-1]
    sma200_last = df["SMA200"].iloc[-1] if "SMA200" in df else np.nan
    out["above_200"] = bool(pd.notna(sma200_last) and last_c > sma200_last)
    
    high_20 = df["High"].rolling(20, min_periods=1).max().shift(1).iloc[-1] if len(df) >= 2 else last_c
    out["breakout_20"] = bool(pd.notna(high_20) and last_c > high_20)
    return out

def get_signal_label(score):
    if score >= 75: return "GÜÇLÜ POZİTİF", "bgreen"
    elif score >= 60: return "POZİTİF", "bgreen"
    elif score >= 45: return "NÖTR / DENGELİ", "byellow"
    elif score >= 30: return "ZAYIF", "bred"
    else: return "GÜÇLÜ NEGATİF", "bred"

def analyze(df, fundamental=75, valuation=70, sector=75, news=70, macro=65, risk=60):
    df = add_indicators(df)
    tech = technical_score(df)
    mom = momentum_score(df)
    trend = trend_score(df)
    support, resistance = support_resistance(df)
    
    weights = {
        "technical": 0.18, "momentum": 0.13, "trend": 0.12,
        "fundamental": 0.17, "valuation": 0.12, "sector": 0.10,
        "news": 0.10, "macro": 0.05, "risk": 0.03
    }
    vals = [tech, mom, trend, fundamental, valuation, sector, news, macro, risk]
    total = round(float(np.dot(vals, list(weights.values()))), 1)

    signal_text, signal_class = get_signal_label(total)

    last_price = float(df["Close"].iloc[-1])
    prev_price = float(df["Close"].iloc[-2]) if len(df) > 1 else last_price
    change_pct = float(((last_price / prev_price) - 1) * 100) if prev_price != 0 else 0.0

    return {
        "last_price": last_price,
        "change_pct": change_pct,
        "technical": tech,
        "momentum": mom,
        "trend": trend,
        "fundamental": fundamental,
        "valuation": valuation,
        "sector": sector,
        "news": news,
        "macro": macro,
        "risk": risk,
        "total": total,
        "signal_text": signal_text,
        "signal_class": signal_class,
        "support": support,
        "resistance": resistance,
        "signals": crossover_flags(df)
    }
