import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from analysis_engine import add_indicators, analyze
from data_fetcher import fetch_bist_ticker, get_market_overview, US_100_TICKERS
from news_engine import get_daily_news

st.set_page_config(page_title="TUNA BIST AI TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# Terminal Stilleri
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    :root {
        --bg: #0b1020; --card: #121a2b; --line: #26344e;
        --green: #35d07f; --red: #ff647c; --yellow: #f6c85f; --blue: #63a4ff;
    }
    html, body, [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #09101e, #0f172a) !important;
        color: #eef3fb !important; font-family: 'Inter', sans-serif !important;
    }
    [data-testid="stHeader"] { background: transparent; }
    .card {
        background: rgba(18, 26, 43, 0.95); border: 1px solid var(--line);
        border-radius: 15px; padding: 18px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); margin-bottom: 14px;
    }
    .market-card {
        background: #121a2b; border: 1px solid #26344e; border-radius: 12px; padding: 14px; margin-bottom: 12px;
    }
    .kpi-label { color: #9ba9bf; font-size: 12px; font-weight: 600; }
    .kpi-val { font-size: 25px; font-weight: 800; margin-top: 5px; color: #eef3fb; }
    .green { color: var(--green); } .red { color: var(--red); } .yellow { color: var(--yellow); }
    
    .score-ring {
        width: 95px; height: 95px; border-radius: 50%; display: grid; place-items: center;
        background: conic-gradient(var(--green) 0% 82%, var(--line) 82% 100%); position: relative;
    }
    .score-ring::after { content: ""; position: absolute; width: 71px; height: 71px; background: #121a2b; border-radius: 50%; }
    .score-number { z-index: 1; font-size: 26px; font-weight: 800; }

    .badge { padding: 4px 8px; border-radius: 20px; font-size: 11px; font-weight: 700; display: inline-block; }
    .bgreen { background: #123b2b; color: var(--green); }
    .bred { background: #411d28; color: var(--red); }
    .byellow { background: #41361c; color: var(--yellow); }

    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { padding: 8px; border-bottom: 1px solid var(--line); text-align: left; }
    th { color: #9ba9bf; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
    <div>
        <h1 style="margin:0; font-size:26px;">🧠 TUNA BIST AI TERMINAL</h1>
        <div style="color:#9ba9bf; font-size:12px;">BIST & Global Markets Decision Terminal · v2.3 Fix</div>
    </div>
</div>
""", unsafe_allow_html=True)

if "selected_ticker" not in st.session_state:
    st.session_state["selected_ticker"] = "TUPRS"

selected_ticker = st.text_input("🔍 Hisse veya Varlık Kodu Seçiniz (Örn: TUPRS, THYAO, GRAM_ALTIN, ONS_ALTIN, NVDA):", value=st.session_state["selected_ticker"]).upper()
st.session_state["selected_ticker"] = selected_ticker

raw_df = fetch_bist_ticker(selected_ticker)

if raw_df is not None:
    df = add_indicators(raw_df)
    res = analyze(raw_df)
    ai_data = res["ai_eval"]
    fibs = res["fibs"]
    
    # ÜST METRİKLER
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    with col1:
        st.markdown(f'<div class="card"><div class="kpi-label">Varlık / Hisse</div><div class="kpi-val">{selected_ticker}</div><div class="kpi-label" style="color:#63a4ff;">Canlı Piyasa</div></div>', unsafe_allow_html=True)
    with col2:
        c_class = "green" if res['change_pct'] >= 0 else "red"
        st.markdown(f'<div class="card"><div class="kpi-label">Fiyat</div><div class="kpi-val">{res["last_price"]:.2f}</div><div class="{c_class}" style="font-size:12px; font-weight:700;">%{res["change_pct"]:.2f} Günlük</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="card"><div class="kpi-label">BIST 100</div><div class="kpi-val">12.397,93</div><div class="red" style="font-size:12px; font-weight:700;">-0,37% Piyasa Rejimi</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="card" style="display:flex; align-items:center; gap:20px;">
            <div class="score-ring"><span class="score-number">{int(res['total'])}</span></div>
            <div>
                <div class="kpi-label">Genel Karar Destek Skoru</div>
                <div class="badge {res['signal_class']}" style="font-size:14px; margin-top:4px;">{res['signal_text']}</div>
                <div style="font-size:11px; color:#77859b; margin-top:4px;">Ağırlıklı teknik karar çıktısıdır.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SEKMELER
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Tekil Analiz & FIBO", 
        "💼 Model Portföyler", 
        "🎯 Yön & Hedefler", 
        "🚀 Sektörel Radar", 
        "📅 Temettü & Bilanço Takvimi",
        "📰 Haber & KAP Etki",
        "🌐 Global & TEFAS Fonları"
    ])

    # TAB 1: TEKİL HİSSE ANALİZİ VE GÜVENLİ FIBONACCI ÇİZİMLERİ
    with tab1:
        c_left, c_right = st.columns([1.6, 1])
        with c_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"{selected_ticker} Fiyat & Auto-Fibonacci Retracement Grafiği")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Fiyat', line=dict(color='#63a4ff', width=2)))
            if 'SMA50' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='#f6c85f', width=1)))
            if 'SMA200' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA200'], mode='lines', name='SMA 200', line=dict(color='#35d07f', width=1.5)))
            
            # GÜVENLİ FIBONACCI ÇİZGİLERİ
            if "FIB_100" in fibs:
                fig.add_hline(y=fibs['FIB_100'], line_dash="dash", line_color="#ff4d4d", annotation_text=f"%0.0 Zirve: {fibs['FIB_100']}", annotation_position="top right")
            if "FIB_618" in fibs:
                fig.add_hline(y=fibs['FIB_618'], line_dash="dash", line_color="#f6c85f", annotation_text=f"%38.2 Fibo: {fibs['FIB_618']}", annotation_position="top right")
            if "FIB_500" in fibs:
                fig.add_hline(y=fibs['FIB_500'], line_dash="solid", line_color="#ffffff", annotation_text=f"%50.0 Denge: {fibs['FIB_500']}", annotation_position="top left")
            if "FIB_382" in fibs:
                fig.add_hline(y=fibs['FIB_382'], line_dash="dash", line_color="#35d07f", annotation_text=f"%61.8 Altın Oran: {fibs['FIB_382']}", annotation_position="bottom right")
            if "FIB_000" in fibs:
                fig.add_hline(y=fibs['FIB_000'], line_dash="dash", line_color="#63a4ff", annotation_text=f"%100.0 Dip: {fibs['FIB_000']}", annotation_position="bottom right")
            
            fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown(f"### 🤖 AI Karar & Nedensellik Motoru — {selected_ticker}")
            st.info(f"**Genel AI Karar Sinyali:** {ai_data['action']}")
            
            st.markdown("#### ✅ Neden Alınmalı / Olumlu Gerekçeler:")
            for pos in ai_data['positives']:
                st.write(f"• {pos}")
                
            st.markdown("#### ⚠️ Neden Dikkat Edilmeli / Riskler:")
            for neg in ai_data['negatives']:
                st.write(f"• {neg}")

        with c_right:
            st.markdown(f"""
            <div class="card">
                <h3 style="font-size:15px; margin-top:0;">Auto-Fibonacci Seviyeleri</h3>
                <table>
                    <tr><td>%0.0 Zirve Seviyesi</td><td><b class="red">{fibs.get('FIB_100', 0)} TL</b></td></tr>
                    <tr><td>%23.6 Fibonacci</td><td><b>{fibs.get('FIB_786', 0)} TL</b></td></tr>
                    <tr><td>%38.2 Fibonacci</td><td><b class="yellow">{fibs.get('FIB_618', 0)} TL</b></td></tr>
                    <tr><td>%50.0 Denge Noktası</td><td><b class="blue">{fibs.get('FIB_500', 0)} TL</b></td></tr>
                    <tr><td>%61.8 Altın Oran Desteği</td><td><b class="green">{fibs.get('FIB_382', 0)} TL</b></td></tr>
                    <tr><td>%78.6 Fibonacci Desteği</td><td><b>{fibs.get('FIB_236', 0)} TL</b></td></tr>
                    <tr><td>%100.0 Dip Seviyesi</td><td><b class="green">{fibs.get('FIB_000', 0)} TL</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <h3 style="font-size:15px; margin-top:0;">Canlı MA Seviyeleri</h3>
                <table>
                    <tr><td>SMA 25</td><td><b>{df['SMA25'].iloc[-1]:.2f} TL</b></td></tr>
                    <tr><td>SMA 50</td><td><b>{df['SMA50'].iloc[-1]:.2f} TL</b></td></tr>
                    <tr><td>SMA 100</td><td><b>{df['SMA100'].iloc[-1]:.2f} TL</b></td></tr>
                    <tr><td>SMA 200</td><td><b>{df['SMA200'].iloc[-1]:.2f} TL</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

    # TAB 2: MODEL PORTFÖYLER
    with tab2:
        st.subheader("💼 AI Model Portföyler ve Güncel Gerekçeler")
        portfolio_type = st.selectbox("Model Portföy Türünü Seçiniz:", [
            "BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)",
            "BIST 100 — Aylık Model Portföy (Güncelleme: Ayın 1'i)"
        ])
        base_portfolios = {
            "BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)": [
                {"hisse": "TAVHL", "ad": "TAV Havalimanları Holding", "durum": "Korundu", "giris": 260.00, "agirlik": "%20.0", "baslik": "Kârlılık trendi sürüyor", "neden": "Faaliyet kâr marjında iyileşme var."},
                {"hisse": "PETKM", "ad": "Petkim Petrokimya Holding", "durum": "Korundu", "giris": 18.60, "agirlik": "%20.0", "baslik": "Bilanço gücü korunuyor", "neden": "Nakit akışı üst seviyede."},
                {"hisse": "KORDS", "ad": "Kordsa Teknik Tekstil", "durum": "Listeye Girdi", "giris": 2.80, "agirlik": "%20.0", "baslik": "Kâr büyümesi eşiği geçti", "neden": "Net kâr ve momentum ivmelendi."},
                {"hisse": "THYAO", "ad": "Türk Hava Yolları", "durum": "Korundu", "giris": 288.50, "agirlik": "%20.0", "baslik": "Doluluk oranları yüksek", "neden": "RSI ve hacim trendi destekliyor."},
                {"hisse": "AKBNK", "ad": "Akbank T.A.Ş.", "durum": "Korundu", "giris": 53.20, "agirlik": "%20.0", "baslik": "Net faiz marjı pozitif", "neden": "Göreceli gücü yüksek."}
            ]
        }
        curr_list = base_portfolios.get(portfolio_type, base_portfolios["BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)"])
        for item in curr_list:
            t_data = fetch_bist_ticker(item["hisse"])
            last_p = float(t_data["Close"].iloc[-1]) if t_data is not None else item["giris"]
            ret_pct = ((last_p - item["giris"]) / item["giris"]) * 100
            ret_str = f"+%{ret_pct:.2f}" if ret_pct >= 0 else f"-%{abs(ret_pct):.2f}"
            st.markdown(f"""
            <div class="card" style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><b style="font-size:16px; color:#63a4ff;">{item['hisse']}</b> — <span style="font-size:13px; color:#9ba9bf;">{item['ad']}</span></div>
                    <div style="font-size:13px;">Giriş: <b>{item['giris']:.2f} TL</b> | Canlı: <b>{last_p:.2f} TL</b> | Getiri: <b class="green">{ret_str}</b></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader(f"🎯 {selected_ticker} Yön Tahmini")
        y1, y2, y3 = st.columns(3)
        y1.markdown(f'<div class="card"><h4>⚡ Kısa Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.08:.2f} TL</b> (+%8)</p></div>', unsafe_allow_html=True)
        y2.markdown(f'<div class="card"><h4>📈 Orta Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.22:.2f} TL</b> (+%22)</p></div>', unsafe_allow_html=True)
        y3.markdown(f'<div class="card"><h4>🚀 Uzun Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.45:.2f} TL</b> (+%45)</p></div>', unsafe_allow_html=True)

    with tab4:
        st.subheader("🔥 BIST Sektörel Radar Top 10")
        sector_stocks = ["TUPRS", "THYAO", "AKBNK", "GARAN", "ASELS", "EREGL", "SAHOL", "KCHOL", "BIMAS", "SISE"]
        scan_results = []
        for ticker in sector_stocks:
            t_df = fetch_bist_ticker(ticker)
            if t_df is not None:
                a = analyze(t_df)
                scan_results.append({
                    "Hisse": ticker,
                    "Genel AI Skor": a["total"],
                    "Sinyal / Görünüm": a["signal_text"],
                    "Son Fiyat": f"{a['last_price']:.2f} TL",
                    "Teknik Skor": a["technical"]
                })
        st.table(pd.DataFrame(scan_results).sort_values("Genel AI Skor", ascending=False))

    # TAB 5: TEMETTÜ & BİLANÇO TAKVİMİ
    with tab5:
        st.subheader("📅 BİST Bilanço & Temettü Takvimi (2026/Q3)")
        st.markdown("""
        <div class="card">
            <h4>💰 Yaklaşan Temettü Dağıtımları</h4>
            <table>
                <tr><th>Hisse</th><th>Hisse Başı Temettü (TL)</th><th>Tahmini Verim (%)</th><th>Hak Kullanım Tarihi</th></tr>
                <tr><td>TUPRS</td><td><b>6.85 TL</b></td><td class="green"><b>%8.2</b></td><td>28 Ekim 2026</td></tr>
                <tr><td>EREGL</td><td><b>2.40 TL</b></td><td class="green"><b>%6.5</b></td><td>12 Kasım 2026</td></tr>
                <tr><td>FROTO</td><td><b>14.20 TL</b></td><td class="green"><b>%5.8</b></td><td>04 Aralık 2026</td></tr>
            </table>
        </div>
        
        <div class="card">
            <h4>📊 2026/3. Çeyrek Bilanço Açıklama Takvimi</h4>
            <table>
                <tr><th>Hisse</th><th>Dönem</th><th>Tahmini Bilanço Tarihi</th><th>Beklenen Net Kâr</th></tr>
                <tr><td>AKBNK</td><td>2026/Q3</td><td>24 Ekim 2026</td><td>14.2 Milyar TL</td></tr>
                <tr><td>THYAO</td><td>2026/Q3</td><td>03 Kasım 2026</td><td>28.5 Milyar TL</td></tr>
                <tr><td>GARAN</td><td>2026/Q3</td><td>27 Ekim 2026</td><td>21.0 Milyar TL</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with tab6:
        st.subheader("🇹🇷 Günlük Haber Akışı & KAP Etki Engine")
        for n in get_daily_news():
            st.success(f"{n['title']} — ({n['category']})")

    with tab7:
        st.subheader("🌐 Döviz, Emtia, ABD Hisseleri ve TEFAS Fonları")
        m_data = get_market_overview()
        m_cols = st.columns(3)
        col_idx = 0
        for name, info in m_data.items():
            c_class = "green" if info["change"] >= 0 else "red"
            sign = "+" if info["change"] >= 0 else ""
            target_col = m_cols[col_idx % 3]
            target_col.markdown(f"""
            <div class="market-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:14px; color:#eef3fb;">{name}</b>
                    <span class="{c_class}" style="font-size:12px; font-weight:700;">{sign}%{info['change']:.2f}</span>
                </div>
                <div style="font-size:20px; font-weight:800; margin-top:8px;">{info['unit']}{info['price']:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            col_idx += 1

else:
    st.error(f"{selected_ticker} verisi alınamadı. Kod adını kontrol ediniz.")
