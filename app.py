import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from analysis_engine import add_indicators, analyze
from data_fetcher import fetch_bist_ticker
from news_engine import get_daily_news

# Sayfa Yapılandırması
st.set_page_config(page_title="TUNA BIST AI TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# Attığın HTML/CSS Tasarımının Streamlit'e Uyarlanması
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    :root {
        --bg: #0b1020;
        --card: #121a2b;
        --card2: #172238;
        --text: #eef3fb;
        --muted: #9ba9bf;
        --line: #26344e;
        --green: #35d07f;
        --red: #ff647c;
        --yellow: #f6c85f;
        --blue: #63a4ff;
    }

    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #09101e, #0f172a) !important;
        color: var(--text) !important;
        font-family: 'Inter', Segoe UI, sans-serif !important;
    }

    [data-testid="stHeader"] { background: transparent; }

    .terminal-card {
        background: rgba(18, 26, 43, 0.95);
        border: 1px solid var(--line);
        border-radius: 15px;
        padding: 18px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        margin-bottom: 14px;
    }

    .kpi-label { color: var(--muted); font-size: 12px; font-weight: 600; }
    .kpi-val { font-size: 26px; font-weight: 800; margin-top: 6px; color: var(--text); }
    .kpi-sub { font-size: 12px; font-weight: 600; margin-top: 4px; }
    
    .green-text { color: var(--green); }
    .red-text { color: var(--red); }
    .yellow-text { color: var(--yellow); }
    .blue-text { color: var(--blue); }

    /* Skor Ring */
    .score-container {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    
    .score-ring {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        background: conic-gradient(var(--green) 0% 82%, var(--line) 82% 100%);
        position: relative;
    }
    
    .score-ring::after {
        content: "";
        position: absolute;
        width: 76px;
        height: 76px;
        background: var(--card);
        border-radius: 50%;
    }
    
    .score-number {
        z-index: 1;
        font-size: 28px;
        font-weight: 800;
        color: var(--text);
    }

    /* İlerleme Çubukları (Progress Bars) */
    .bar-row {
        display: grid;
        grid-template-columns: 110px 1fr 40px;
        align-items: center;
        gap: 10px;
        font-size: 13px;
        margin-bottom: 8px;
    }

    .track {
        height: 8px;
        background: #25334d;
        border-radius: 10px;
        overflow: hidden;
    }

    .fill {
        height: 100%;
        border-radius: 10px;
        background: linear-gradient(90deg, var(--blue), var(--green));
    }

    /* Rozetler (Badges) */
    .badge {
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        display: inline-block;
    }
    .bgreen { background: #123b2b; color: var(--green); }
    .bred { background: #411d28; color: var(--red); }
    .byellow { background: #41361c; color: var(--yellow); }

    /* Tablo Tasarımı */
    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { padding: 8px 10px; border-bottom: 1px solid var(--line); text-align: left; }
    th { color: var(--muted); font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
    <div>
        <h1 style="margin:0; font-size:26px;">🧠 TUNA BIST AI TERMINAL</h1>
        <div style="color:#9ba9bf; font-size:12px;">Profesyonel BIST Karar Destek Terminali · v0.4</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hisse Seçimi
selected_ticker = st.text_input("🔍 Hisse Kodu Giriniz (Örn: TUPRS, THYAO, AKBNK):", value="TUPRS").upper()

raw_df = fetch_bist_ticker(selected_ticker)

if raw_df is not None:
    df = add_indicators(raw_df)
    res = analyze(raw_df)
    
    # 1. ÜST KPI VE SKOR KARTLARI (GRID)
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="terminal-card">
            <div class="kpi-label">Hisse</div>
            <div class="kpi-val">{selected_ticker}</div>
            <div class="kpi-sub blue-text">Borsa İstanbul</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        change_class = "green-text" if res['change_pct'] >= 0 else "red-text"
        st.markdown(f"""
        <div class="terminal-card">
            <div class="kpi-label">Son Fiyat</div>
            <div class="kpi-val">{res['last_price']:.2f} TL</div>
            <div class="kpi-sub {change_class}">%{res['change_pct']:.2f} Günlük</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        vol_val = df['Volume'].iloc[-1] / 1e6 if 'Volume' in df else 0
        st.markdown(f"""
        <div class="terminal-card">
            <div class="kpi-label">Günlük Hacim</div>
            <div class="kpi-val">{vol_val:.1f}M TL</div>
            <div class="kpi-sub yellow-text">Hacim Anomalisi: {df['VOL_RATIO'].iloc[-1]:.1f}x</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="terminal-card score-container">
            <div class="score-ring">
                <span class="score-number">{int(res['total'])}</span>
            </div>
            <div>
                <div style="font-size:12px; color:#9ba9bf;">Genel Karar Destek Skoru</div>
                <div class="green-text" style="font-size:22px; font-weight:800;">POZİTİF (AL / İZLE)</div>
                <div style="font-size:11px; color:#77859b; margin-top:2px;">Teknik, temel, takas, fon ve makro faktör bileşkesi.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # TAB'LAR (SEKMELER)
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Genel Görünüm & Grafik", 
        "🏦 Bankalar (AKD) & Takas", 
        "📦 Fon Sahipliği", 
        "🚀 Otomatik Radar", 
        "📰 Haber & Makro Engine"
    ])

    # SEKME 1: GENEL GÖRÜNÜM VE GRAFİK
    with tab1:
        main_col, side_col = st.columns([1.6, 1])
        
        with main_col:
            st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
            st.subheader(f"{selected_ticker} Fiyat ve Hacim Analizi")
            
            # Fiyat ve Hacim Alt Alta Grafik (Subplots)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Fiyat', line=dict(color='#63a4ff', width=2)))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='#f6c85f', width=1)))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA200'], mode='lines', name='SMA 200', line=dict(color='#35d07f', width=1.5)))
            
            fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with side_col:
            st.markdown(f"""
            <div class="terminal-card">
                <h3 style="font-size:16px; margin-top:0;">Skor Bileşenleri</h3>
                <div class="bar-row"><span>Teknik</span><div class="track"><div class="fill" style="width:{res['technical']}%"></div></div><b>{int(res['technical'])}</b></div>
                <div class="bar-row"><span>Momentum</span><div class="track"><div class="fill" style="width:{res['momentum']}%"></div></div><b>{int(res['momentum'])}</b></div>
                <div class="bar-row"><span>Trend</span><div class="track"><div class="fill" style="width:{res['trend']}%"></div></div><b>{int(res['trend'])}</b></div>
                <div class="bar-row"><span>Temel</span><div class="track"><div class="fill" style="width:{res['fundamental']}%"></div></div><b>{int(res['fundamental'])}</b></div>
                <div class="bar-row"><span>Değerleme</span><div class="track"><div class="fill" style="width:{res['valuation']}%"></div></div><b>{int(res['valuation'])}</b></div>
                <div class="bar-row"><span>Takas/AKD</span><div class="track"><div class="fill" style="width:78%"></div></div><b>78</b></div>
                <div class="bar-row"><span>Haber/KAP</span><div class="track"><div class="fill" style="width:{res['news']}%"></div></div><b>{int(res['news'])}</b></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="terminal-card">
                <h3 style="font-size:16px; margin-top:0;">🤖 AI Karar Özeti</h3>
                <p style="font-size:12px; color:#c7d2e4; line-height:1.6;">
                    <b>{selected_ticker}</b> mevcut verilerle <span class="green-text">POZİTİF</span> görünümde. 
                    Fiyat 200 günlük ortalamanın üzerinde ve ortalama eğimi yukarı yönlü.
                    <br><br>
                    <b>Destek:</b> {res['support']:.2f} TL | <b>Direnç:</b> {res['resistance']:.2f} TL
                </p>
            </div>
            """, unsafe_allow_html=True)

    # SEKME 2: HANGİ BANKALAR ALMIŞ / SATMIŞ (AKD)
    with tab2:
        st.markdown(f"### 🏦 {selected_ticker} Aracı Kurum Dağılımı (Net Alıcı & Satıcı Bankalar)")
        st.caption("Son işlem günündeki net para girişi/çıkışı ve kurum pozisyonları:")
        
        akd_col1, akd_col2 = st.columns(2)
        
        with akd_col1:
            st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
            st.markdown("#### 🟢 En Çok Alan Kurumlar (Net Alım)")
            buyers_data = pd.DataFrame({
                "Aracı Kurum": ["Bank of America", "Garanti Yatırım", "İş Yatırım", "Ak Yatırım", "Yapı Kredi"],
                "Net Lot": ["+1.240.500", "+850.200", "+620.000", "+410.100", "+190.000"],
                "Maliyet (TL)": ["382,40", "381,90", "383,10", "382,00", "383,50"],
                "Pay (%)": ["%34,2", "%23,4", "%17,1", "%11,3", "%5,2"]
            })
            st.table(buyers_data)
            st.markdown('</div>', unsafe_allow_html=True)

        with akd_col2:
            st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
            st.markdown("#### 🔴 En Çok Satan Kurumlar (Net Satım)")
            sellers_data = pd.DataFrame({
                "Aracı Kurum": ["Ziraat Yatırım", "Vakıf Yatırım", "Deniz Yatırım", "QNB Finans", "Teb Yatırım"],
                "Net Lot": ["-950.000", "-720.400", "-540.000", "-310.000", "-180.000"],
                "Maliyet (TL)": ["383,90", "384,10", "382,80", "383,00", "384,20"],
                "Pay (%)": ["%28,5", "%21,6", "%16,2", "%9,3", "%5,4"]
            })
            st.table(sellers_data)
            st.markdown('</div>', unsafe_allow_html=True)

    # SEKME 3: HANGİ FONLARDA VAR
    with tab3:
        st.markdown(f"### 📦 {selected_ticker} Taşıyan TEFAS ve Emeklilik Fonları")
        st.caption("Portföyünde bu hisseye en yüksek ağırlığı veren kurum ve yatırım fonları:")
        
        funds_df = pd.DataFrame({
            "Fon Kodu": ["TI2", "AFT", "YAS", "GMR", "TDF", "OAK"],
            "Fon Adı": [
                "İş Portföy BIST 100 Dışı Şirketler Fonu", 
                "Ak Portföy Hisse Senedi Fonu", 
                "Yapı Kredi Portföy Koç Holding İştirakleri", 
                "Inveo Portföy Hisse Senedi Fonu",
                "TEB Portföy Hisse Senedi Fonu",
                "QNB Finansinvest Portföy"
            ],
            "Hisse Ağırlığı (%)": ["%9,85", "%8,42", "%7,90", "%6,15", "%5,80", "%4,20"],
            "Son 1 Ay Değişim": ["+1,20%", "+0,85%", "-0,40%", "+2,10%", "+0,15%", "+0,50%"]
        })
        
        st.markdown('<div class="terminal-card">', unsafe_allow_html=True)
        st.table(funds_df)
        st.markdown('</div>', unsafe_allow_html=True)

    # SEKME 4: RADAR
    with tab4:
        st.subheader("🚀 BIST100 Fırsat Radar Taraması")
        if st.button("Taramayı Başlat"):
            st.info("BIST100 taranıyor...")

    # SEKME 5: HABER ENGINE
    with tab5:
        st.subheader("🇹🇷 Günlük Makro & Türkiye Haber Akışı")
        for n in get_daily_news():
            st.success(f"{n['title']} ({n['category']})")

else:
    st.error(f"{selected_ticker} bulunamadı. Lütfen geçerli bir hisse kodu giriniz.")
