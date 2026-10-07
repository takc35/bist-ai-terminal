import numpy as np
import pandas as pd

def pivot_points(df):
    """
    Klasik Pivot ve Ara Destek/Direnç Seviyeleri (S2, S1, PP, R1, R2)
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

def get_ai_reasoning(df, res):
    """
    Şunu al / bunu alma gerekçeli detaylı AI yorum motoru.
    """
    last_p = res["last_price"]
    positives = []
    negatives = []
    
    # Trend ve MA Kontrolleri
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
        positives.append(f"RSI ({rsi_val:.1f}) dengeli bölgede; ne aşırı alımda ne aşırı satımda, yükseliş marjı var.")
    elif rsi_val > 70:
        negatives.append(f"RSI ({rsi_val:.1f}) aşırı alım (overbought) bölgesinde; kısa vadeli düzeltme riski yüksek.")
    elif rsi_val < 35:
        positives.append(f"RSI ({rsi_val:.1f}) dip seviyelerde; tepki alımı olasılığı artıyor.")

    p_levels = pivot_points(df)
    if last_p >= p_levels["R1"]:
        negatives.append(f"Ara direnç seviyesi olan {p_levels['R1']} TL yakınında, kâr satışları görülebilir.")
    if last_p <= p_levels["S1"]:
        positives.append(f"Ara destek seviyesi olan {p_levels['S1']} TL civarında tepki alımları beklenebilir.")

    return positives, negatives, p_levels
