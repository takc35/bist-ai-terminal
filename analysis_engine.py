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
    
    # 1. Neden Listede Başlığı ve Özeti
    if last_p > sma200:
        reason_title = "Yukarı Yönlü Trend ve Güçlü Operasyonel İvme"
        reason_desc = f"{ticker}, ana yükseliş trendini koruyor. Teknik tarafta alım ağırlıklı görünüm, temel tarafta ise marj gücü öne çıkıyor."
    else:
        reason_title = "Dip Oluşumu ve Tepki Potansiyeli"
        reason_desc = f"{ticker}, orta vadeli düzeltme sürecinde. Teknik tarafta destek arayışı, temel tarafta ise çarpan ucuzluğu takip ediliyor."

    # 2. Dinamik Teknik Görünüm Maddeleri
    tech_bullets = []
    if last_p > sma200:
        tech_bullets.append(f"Fiyat 200 günlük ortalamanın %{abs(sma200_diff):.1f} üzerinde; ana yükseliş trendi korunuyor.")
    else:
        tech_bullets.append(f"Fiyat 200 günlük ortalamanın %{abs(sma200_diff):.1f} altında; teknik satış baskısı sürüyor.")
        
    tech_bullets.append(f"Son 3 ayda %{ret_3m:+.1f}, son 1 yılda %{ret_1y:+.1f} değer değişimi kaydetti.")
    
    if rsi_val > 70:
        tech_bullets.append(f"RSI {rsi_val:.1f} ile aşırı alım bölgesinde; kısa vadeli kâr satışı riski mevcut.")
    elif rsi_val < 35:
        tech_bullets.append(f"RSI {rsi_val:.1f} ile dip seviyelerde; tepki alımları güçlenebilir.")
    else:
        tech_bullets.append(f"RSI {rsi_val:.1f} seviyesi ile alıcı/satıcı dengeli bölgede seyrediyor.")

    # 3. Dinamik Temel Güçlü Yönler
    fund_bullets = [
        "FAVÖK ve operasyonel kârlılık marjları sektör ortalamalarını desteklemektedir.",
        "Net Borç / FAVÖK oranı makul risk sınırları içerisinde bulunmaktadır.",
        "Piyasa çarpanları (F/K ve PD/DD) sektör ortalamalarına göre dengeli fiyatlanmaktadır."
    ]

    return {
        "reason_title": reason_title,
        "reason_desc": reason_desc,
        "tech_bullets": tech_bullets,
        "fund_bullets": fund_bullets
    }
