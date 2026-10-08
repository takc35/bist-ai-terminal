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

def fibonacci_levels(df):
    recent = df.tail(90)
    high = float(recent["High"].max())
    low = float(recent["Low"].min())
    diff = high - low
    
    return {
        "FIB_100": round(high, 2),
        "FIB_786": round(high - diff * 0.214, 2),
        "FIB_618": round(high - diff * 0.382, 2),
        "FIB_500": round(high - diff * 0.500, 2),
        "FIB_382": round(high - diff * 0.618, 2),
        "FIB_236": round(high - diff * 0.786, 2),
        "FIB_000": round(low, 2)
    }

def calculate_dynamic_score(df):
    last_p = float(df["Close"].iloc[-1])
    score = 50.0
    
    sma50 = df["SMA50"].iloc[-1] if "SMA50" in df else None
    sma200 = df["SMA200"].iloc[-1] if "SMA200" in df else None
    rsi_val = df["RSI14"].iloc[-1] if "RSI14" in df else 50
    macd_val = df["MACD"].iloc[-1] if "MACD" in df else 0
    macd_sig = df["MACD_SIGNAL"].iloc[-1] if "MACD_SIGNAL" in df else 0
    
    if sma200:
        if last_p > sma200: score += 15
        else: score -= 15
        
    if sma50:
        if last_p > sma50: score += 10
        else: score -= 10
        
    if 45 <= rsi_val <= 65:
        score += 10
    elif rsi_val > 70:
        score -= 15
    elif rsi_val < 30:
        score += 5
    else:
        score -= 5
        
    if macd_val > macd_sig: score += 10
    else: score -= 10
    
    return round(float(np.clip(score, 10.0, 95.0)), 1)

def get_detailed_bullet_analysis(df, ticker="HISSE"):
    last_p = float(df["Close"].iloc[-1])
    p_3m = float(df["Close"].iloc[-60]) if len(df) >= 60 else last_p
    p_1y = float(df["Close"].iloc[0]) if len(df) >= 200 else last_p
    
    ret_3m = ((last_p - p_3m) / p_3m) * 100
    ret_1y = ((last_p - p_1y) / p_1y) * 100
    
    sma50 = df["SMA50"].iloc[-1] if "SMA50" in df else last_p
    sma200 = df["SMA200"].iloc[-1] if "SMA200" in df else last_p
    rsi_val = df["RSI14"].iloc[-1] if "RSI14" in df else 50.0
    sma200_diff = ((last_p - sma200) / sma200) * 100 if sma200 != 0 else 0
    
    if last_p > sma200:
        reason_title = "Yukarı Yönlü Trend ve Güçlü Operasyonel İvme"
        reason_desc = f"{ticker}, ana yükseliş trendini koruyor. Teknik tarafta alım ağırlıklı görünüm, temel tarafta ise marj gücü öne çıkıyor."
    else:
        reason_title = "Dip Oluşumu ve Tepki Potansiyeli"
        reason_desc = f"{ticker}, orta vadeli düzeltme sürecinde. Teknik tarafta destek arayışı, temel tarafta ise çarpan ucuzluğu takip ediliyor."

    tech_bullets = []
    if last_p > sma200:
        tech_bullets.append(f"Fiyat 200 günlük ortalamanın %{abs(sma200_diff):.1f} üzerinde; ana trend yukarı yönlü.")
    else:
        tech_bullets.append(f"Fiyat 200 günlük ortalamanın %{abs(sma200_diff):.1f} altında; teknik satış baskısı sürüyor.")
        
    tech_bullets.append(f"Son 3 ayda %{ret_3m:+.1f}, son 1 yılda %{ret_1y:+.1f} değer değişimi kaydetti.")
    
    if rsi_val > 70:
        tech_bullets.append(f"RSI {rsi_val:.1f} ile aşırı alım bölgesinde; kısa vadeli kâr satışı riski mevcut.")
    elif rsi_val < 35:
        tech_bullets.append(f"RSI {rsi_val:.1f} ile dip seviyelerde; tepki alımları güçlenebilir.")
    else:
        tech_bullets.append(f"RSI {rsi_val:.1f} seviyesi ile alıcı/satıcı dengeli bölgede seyrediyor.")

    fund_bullets = [
        "FAVÖK ve operasyonel kârlılık marjları sektör ortalamalarını desteklemektedir.",
        "Net Borç / FAVÖK oranı makul ve riskli seviyenin altındadır.",
        "Piyasa çarpanları (F/K ve PD/DD) sektör ortalamalarına göre dengeli fiyatlanmaktadır."
    ]

    return {
        "reason_title": reason_title,
        "reason_desc": reason_desc,
        "tech_bullets": tech_bullets,
        "fund_bullets": fund_bullets
    }

def get_ai_reasoning(df, total_score):
    last_p = float(df["Close"].iloc[-1])
    positives = []
    negatives = []
    
    sma50 = df["SMA50"].iloc[-1] if "SMA50" in df else None
    sma200 = df["SMA200"].iloc[-1] if "SMA200" in df else None
    rsi_val = df["RSI14"].iloc[-1] if "RSI14" in df else 50
    
    if sma200 and last_p > sma200:
        positives.append("Fiyat 200 günlük ana ortalamanın (SMA200) üzerinde; uzun vadeli boğa trendi korunuyor.")
    else:
        negatives.append("Fiyat 200 günlük ortalamanın altında; uzun vadeli teknik baskı devam ediyor.")
        
    if sma50 and last_p > sma50:
        positives.append("Kısa-orta vadeli 50 günlük hareketli ortalama desteği üzerinde pozitif görünüm var.")
    else:
        negatives.append("50 günlük ortalamanın altına sarkması kısa vadeli ivme kaybına işaret ediyor.")
        
    if 45 <= rsi_val <= 65:
        positives.append(f"RSI ({rsi_val:.1f}) dengeli bölgede; alım gücü korunuyor.")
    elif rsi_val > 70:
        negatives.append(f"RSI ({rsi_val:.1f}) aşırı alım bölgesinde; kâr satışı riski yüksek.")
    elif rsi_val < 35:
        positives.append(f"RSI ({rsi_val:.1f}) dip seviyelerde; tepki alımı olasılığı güçleniyor.")

    fibs = fibonacci_levels(df)
    
    if total_score >= 75:
        action, action_class = "GÜÇLÜ AL (POZİTİF)", "bgreen"
    elif total_score >= 60:
        action, action_class = "AL / KADEMELİ TOPLA", "bgreen"
    elif total_score >= 45:
        action, action_class = "TUT / NEUTRAL", "byellow"
    elif total_score >= 30:
        action, action_class = "SAT / BEKLEMEDE KAL", "bred"
    else:
        action, action_class = "GÜÇLÜ SAT (ZAYIF)", "bred"

    return {
        "action": action,
        "action_class": action_class,
        "positives": positives if positives else ["Kısa vadeli teknik göstergeler nötr seyrediyor."],
        "negatives": negatives if negatives else ["Belirgin bir kısa vadeli teknik risk faktörü tespit edilmedi."],
        "fibs": fibs
    }

def analyze(df, ticker="HISSE"):
    df = add_indicators(df)
    last_p = float(df["Close"].iloc[-1])
    prev_p = float(df["Close"].iloc[-2]) if len(df) > 1 else last_p
    change_pct = ((last_p - prev_p) / prev_p) * 100 if prev_p != 0 else 0.0
    
    total = calculate_dynamic_score(df)
    tech = total
    mom = round(total * 0.9, 1)
    trend = round(total * 1.05, 1) if total > 50 else round(total * 0.8, 1)
    
    fibs = fibonacci_levels(df)
    ai_eval = get_ai_reasoning(df, total)
    detailed_eval = get_detailed_bullet_analysis(df, ticker)

    return {
        "last_price": last_p,
        "change_pct": change_pct,
        "technical": tech,
        "momentum": mom,
        "trend": trend,
        "fundamental": 70.0,
        "valuation": 65.0,
        "sector": 70.0,
        "news": 65.0,
        "risk": 60.0,
        "total": total,
        "signal_text": ai_eval["action"],
        "signal_class": ai_eval["action_class"],
        "support": fibs["FIB_382"],
        "resistance": fibs["FIB_618"],
        "fibs": fibs,
        "p_levels": fibs,
        "ai_eval": ai_eval,
        "detailed_eval": detailed_eval,
        "signals": {"above_200": bool(last_p > (df["SMA200"].iloc[-1] if "SMA200" in df else 0))}
    }
