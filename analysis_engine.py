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

def bollinger(close, n=20, k=2):
    mid = sma(close, n)
    std = close.rolling(n).std()
    return mid, mid + k*std, mid - k*std

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
    df["BB_MID"], df["BB_UPPER"], df["BB_LOWER"] = bollinger(c)
    df["ATR14"] = atr(df)
    df["VOL20"] = df["Volume"].rolling(20).mean()
    df["VOL_RATIO"] = df["Volume"] / df["VOL20"]
    df["ROC20"] = c.pct_change(20) * 100
    df["ROC60"] = c.pct_change(60) * 100
    return df

def support_resistance(df, window=20):
    x = df.tail(120)
    support = x["Low"].rolling(window).min().iloc[-1]
    resistance = x["High"].rolling(window).max().iloc[-1]
    return float(support), float(resistance)

def technical_score(df):
    x = df.iloc[-1]
    score = 50.0
    if x["Close"] > x["SMA200"]: score += 15
    else: score -= 15
    if x["Close"] > x["SMA50"]: score += 8
    else: score -= 8
    if x["Close"] > x["SMA25"]: score += 5
    else: score -= 5

    if 50 <= x["RSI14"] <= 68: score += 7
    elif x["RSI14"] < 30: score += 3
    elif x["RSI14"] > 75: score -= 7

    if x["MACD"] > x["MACD_SIGNAL"]: score += 7
    else: score -= 4

    if x["VOL_RATIO"] >= 1.5: score += 5
    elif x["VOL_RATIO"] < 0.7: score -= 2

    return round(float(np.clip(score, 0, 100)), 1)

def momentum_score(df):
    x = df.iloc[-1]
    score = 50.0
    score += np.clip(x["ROC20"], -20, 20) * 0.7
    score += np.clip(x["ROC60"], -30, 30) * 0.35
    if x["MACD"] > x["MACD_SIGNAL"]: score += 7
    if x["Close"] > x["SMA25"]: score += 5
    return round(float(np.clip(score, 0, 100)), 1)

def trend_score(df):
    x = df.iloc[-1]
    mas = [x["SMA25"], x["SMA50"], x["SMA100"], x["SMA200"]]
    valid = [v for v in mas if pd.notna(v)]
    if not valid: return 50.0
    above = sum(x["Close"] > v for v in valid)
    slope_bonus = 5 if x["SMA50"] > df["SMA50"].iloc[-10] else -5
    return round(float(np.clip(25 + 15*above + slope_bonus, 0, 100)), 1)

def crossover_flags(df):
    out = {}
    for a, b, name in [(25, 50, "25_50"), (50, 200, "50_200")]:
        A = df[f"SMA{a}"]
        B = df[f"SMA{b}"]
        out[name+"_golden"] = bool(A.iloc[-1] > B.iloc[-1] and A.iloc[-2] <= B.iloc[-2])
        out[name+"_death"] = bool(A.iloc[-1] < B.iloc[-1] and A.iloc[-2] >= B.iloc[-2])
    out["above_200"] = bool(df["Close"].iloc[-1] > df["SMA200"].iloc[-1])
    out["breakout_20"] = bool(df["Close"].iloc[-1] > df["High"].rolling(20).max().shift(1).iloc[-1])
    return out

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

    return {
        "last_price": float(df["Close"].iloc[-1]),
        "change_pct": float(((df["Close"].iloc[-1] / df["Close"].iloc[-2]) - 1) * 100),
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
        "support": support,
        "resistance": resistance,
        "signals": crossover_flags(df)
    }