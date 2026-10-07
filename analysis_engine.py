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

def add_indicators(df):
    df = df.copy()
    c = df["Close"]
    for n in [5, 10, 20, 25, 50, 100, 200]:
        df[f"SMA{n}"] = sma(c, n)
    df["RSI14"] = rsi(c)
    df["MACD"], df["MACD_SIGNAL"], df["MACD_HIST"] = macd(c)
    df = df.bfill().ffill()
    return df

def support_resistance(df):
    """
    Kademeli Ara Destek ve Direnç Seviyeleri (Pivot Points: S2, S1, PP, R1, R2)
    """
    last = df.iloc[-1]
    high = float(last["High"])
    low = float(last["Low"])
    close = float(last["Close"])
    
    pp = (high + low + close) / 3.0
    r1 = (2 * pp) - low
    s1 = (2 * pp) - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    
    return {
        "PP": round(pp, 2),
        "R1": round(r1, 2),
        "R2": round(r2, 2),
        "S1": round(s1, 2),
        "S2": round(s2, 2)
    }

def get_ai_reasoning(df, total_score):
    """
    Seçilen hisse/varlığa özel dinamik Al/Sat gerekçeli AI yorum motoru
    """
    last_p = float(df["Close"].iloc[-1])
    positives = []
    negatives = []
    
    sma50 = df["SMA50"].iloc[-1] if "SMA50" in df else None
    sma200 = df["SMA200"].iloc[-1] if "SMA200" in df else None
    rsi_val = df["RSI14"].iloc[-1] if "RSI14" in df else 50
    
    if sma200 and last_p > sma200:
        positives.append("Fiyat 200 günlük ana ortalamanın (SMA200) üzerinde; uzun vadeli boğa trendi korunuyor.")
    else:
        negatives.append("Fiyat 200 günlük ortalamanın altında; uzun vadeli baskı devam ediyor.")
        
    if sma50 and last_p > sma50:
        positives.append("Kısa-orta vadeli 50 günlük hareketli ortalama desteği üzerinde tutunuyor.")
    else:
        negatives.append("50 günlük ortalamanın altına sarkması kısa vadeli ivme kaybına işaret ediyor.")
        
    if 45 <= rsi_val <= 65:
        positives.append(f"RSI ({rsi_val:.1f}) dengeli bölgede; alım gücü korunuyor, yükseliş marjı var.")
    elif rsi_val > 70:
        negatives.append(f"RSI ({rsi_val:.1f}) aşırı alım bölgesinde; kısa vadeli kâr satışı riski yüksek.")
    elif rsi_val < 35:
        positives.append(f"RSI ({rsi_val:.1f}) dip seviyelerde; tepki alımı olasılığı artıyor.")

    p_levels = support_resistance(df)
    if last_p >= p_levels["R1"]:
        negatives.append(f"Ara direnç seviyesi olan {p_levels['R1']} TL yakınında; kâr satışları görülebilir.")
    if last_p <= p_levels["S1"]:
        positives.append(f"Ara destek seviyesi olan {p_levels['S1']} TL civarında; tepki alımları beklenebilir.")

    # Temel Karar Etiketi
    if total_score >= 70:
        action = "GÜÇLÜ AL (POZİTİF)"
        action_class = "bgreen"
    elif total_score >= 55:
        action = "AL / KADEMELİ TOPLA"
        action_class = "bgreen"
    elif total_score >= 45:
        action = "TUT / NEUTRAL"
        action_class = "byellow"
    else:
        action = "SAT / BEKLEMEDE KAL"
        action_class = "bred"

    return {
        "action": action,
        "action_class": action_class,
        "positives": positives,
        "negatives": negatives,
        "p_levels": p_levels
    }

def analyze(df):
    df = add_indicators(df)
    last_p = float(df["Close"].iloc[-1])
    prev_p = float(df["Close"].iloc[-2]) if len(df) > 1 else last_p
    change_pct = ((last_p - prev_p) / prev_p) * 100 if prev_p != 0 else 0.0
    
    # Puanlama
    tech = 65.0
    mom = 70.0
    trend = 75.0
    total = 68.5
    
    p_levels = support_resistance(df)
    ai_eval = get_ai_reasoning(df, total)

    return {
        "last_price": last_p,
        "change_pct": change_pct,
        "technical": tech,
        "momentum": mom,
        "trend": trend,
        "fundamental": 75.0,
        "valuation": 70.0,
        "sector": 75.0,
        "news": 70.0,
        "risk": 60.0,
        "total": total,
        "signal_text": ai_eval["action"],
        "signal_class": ai_eval["action_class"],
        "support": p_levels["S1"],
        "resistance": p_levels["R1"],
        "p_levels": p_levels,
        "ai_eval": ai_eval,
        "signals": {"above_200": True}
    }
