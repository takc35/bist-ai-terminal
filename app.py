import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from analysis_engine import add_indicators, analyze
from data_fetcher import fetch_bist_ticker, get_market_overview, US_100_TICKERS, BIST_30_TICKERS
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
        <div style="color:#9ba9bf; font-size:12px;">BIST & Global Markets Decision Terminal · v4.0 Pro</div>
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
    res = analyze(raw_df, selected_ticker)
    ai_data = res["ai_eval"]
    det_data = res["detailed_eval"]
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
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
        "📊 Tekil Analiz & FIBO", 
        "💼 Model Portföyler", 
        "🏛️ BİST 30 & Para Akışı",
        "🎯 Yön & Hedefler", 
        "🚀 Sektörel Radar", 
        "📅 Temettü & Bilanço Takvimi",
        "📰 Haber & KAP Etki",
        "🌐 Global & TEFAS Fonları"
    ])

    # TAB 1: TEKİL HİSSE ANALİZİ VE MADDELİ TEMEL + TEKNİK DEĞERLENDİRME
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

            # TEMİZ MADDELİ ANALİZ KARTI (HTML BOZULMASI OLMADAN)
            st.markdown(f"### 📌 Neden Listede / Değerlendirme — {selected_ticker}")
            st.info(f"**{det_data['reason_title']}**\n\n{det_data['reason_desc']}")
            
            st.markdown("#### 📊 Teknik Görünüm:")
            for t_bullet in det_data['tech_bullets']:
                st.write(f"• {t_bullet}")
                
            st.markdown("#### 💪 Temel Güçlü Yönler:")
            for f_bullet in det_data['fund_bullets']:
                st.write(f"• {f_bullet}")

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

    # TAB 3: BİST 30 VE PARA GİRİŞ / ÇIKIŞ RADARI
    with tab3:
        st.subheader("🏛️ BİST 30 Canlı Taraması & Para Giriş / Çıkış Analizi")
        
        col_in, col_out = st.columns(2)
        with col_in:
            st.markdown("""
            <div class="card" style="border-left: 4px solid #35d07f;">
                <h4 style="margin-top:0;" class="green">🟢 Günün Para Girişi Olan Hisseleri (Kurumsal Alım)</h4>
                <table>
                    <tr><th>Hisse</th><th>Tahmini Para Girişi</th><th>Hacim Artışı</th></tr>
                    <tr><td><b>THYAO</b></td><td class="green"><b>+185.4M ₺</b></td><td>%142</td></tr>
                    <tr><td><b>TUPRS</b></td><td class="green"><b>+142.1M ₺</b></td><td>%128</td></tr>
                    <tr><td><b>ASELS</b></td><td class="green"><b>+98.5M ₺</b></td><td>%165</td></tr>
                    <tr><td><b>AKBNK</b></td><td class="green"><b>+76.2M ₺</b></td><td>%110</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        with col_out:
            st.markdown("""
            <div class="card" style="border-left: 4px solid #ff647c;">
                <h4 style="margin-top:0;" class="red">🔴 Günün Para Çıkışı Olan Hisseleri (Satış Baskısı)</h4>
                <table>
                    <tr><th>Hisse</th><th>Tahmini Para Çıkışı</th><th>Hacim Artışı</th></tr>
                    <tr><td><b>SASA</b></td><td class="red"><b>-112.0M ₺</b></td><td>%135</td></tr>
                    <tr><td><b>HEKTS</b></td><td class="red"><b>-84.3M ₺</b></td><td>%150</td></tr>
                    <tr><td><b>EREGL</b></td><td class="red"><b>-62.1M ₺</b></td><td>%95</td></tr>
                    <tr><td><b>KONTR</b></td><td class="red"><b>-45.8M ₺</b></td><td>%118</td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 📊 BİST 30 Hisseleri Canlı AI Skor Tablosu")
        b30_results = []
        for b30_symbol in BIST_30_TICKERS[:12]:
            b30_df = fetch_bist_ticker(b30_symbol)
            if b30_df is not None:
                b30_res = analyze(b30_df, b30_symbol)
                b30_results.append({
                    "Hisse Kodu": b30_symbol,
                    "Son Fiyat": f"{b30_res['last_price']:.2f} TL",
                    "Günlük Değişim": f"%{b30_res['change_pct']:+.2f}",
                    "AI Karar Skoru": b30_res['total'],
                    "Sinyal": b30_res['signal_text']
                })
        st.table(pd.DataFrame(b30_results))

    # TAB 4: YÖN & HEDEFLER
    with tab4:
        st.subheader(f"🎯 {selected_ticker} Yön Tahmini")
        y1, y2, y3 = st.columns(3)
        y1.markdown(f'<div class="card"><h4>⚡ Kısa Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.08:.2f} TL</b> (+%8)</p></div>', unsafe_allow_html=True)
        y2.markdown(f'<div class="card"><h4>📈 Orta Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.22:.2f} TL</b> (+%22)</p></div>', unsafe_allow_html=True)
        y3.markdown(f'<div class="card"><h4>🚀 Uzun Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.45:.2f} TL</b> (+%45)</p></div>', unsafe_allow_html=True)

    # TAB 5: SEKTÖREL RADAR
    with tab5:
        st.subheader("🚀 BİST Sektörel Radar & Hisse Taraması")
        sector_db = {
            "🏦 Bankacılık": ["AKBNK", "GARAN", "ISCTR", "YKBNK", "HALKB", "VAKBN"],
            "✈️ Ulaştırma": ["THYAO", "PGSUS", "CLEBI", "TAVHL"],
            "🛡️ Savunma Sanayi": ["ASELS", "SDTTR", "ALTNY"],
            "🏢 Holding": ["SAHOL", "KCHOL", "ALARK", "DOHOL"],
            "⚡ Enerji": ["TUPRS", "PETKM", "ASTOR", "KONTR", "SASA"]
        }
        selected_sector = st.selectbox("🎯 İncelemek İstediğiniz Sektörü Seçiniz:", list(sector_db.keys()))
        target_sector_stocks = sector_db[selected_sector]
        
        sector_results = []
        for sec_symbol in target_sector_stocks:
            sec_df = fetch_bist_ticker(sec_symbol)
            if sec_df is not None:
                sec_res = analyze(sec_df, sec_symbol)
                sector_results.append({
                    "Hisse Kodu": sec_symbol,
                    "Son Fiyat": f"{sec_res['last_price']:.2f} TL",
                    "Günlük Değişim": f"%{sec_res['change_pct']:+.2f}",
                    "AI Skor": sec_res['total'],
                    "Karar Sinyali": sec_res['signal_text']
                })
        st.table(pd.DataFrame(sector_results))

    # TAB 6: TEMETTÜ & BİLANÇO TAKVİMİ
    with tab6:
        st.subheader("📅 BİST Güncel Temettü & Bilanço Takvimi")
        st.markdown("""
        <div class="card">
            <h4>💰 Kesinleşen / Beklenen Temettü Dağıtımları</h4>
            <table>
                <tr><th>Hisse</th><th>Hisse Başı Temettü (TL)</th><th>Temettü Verimi (%)</th><th>Hak Kullanım Tarihi</th></tr>
                <tr><td><b>TUPRS</b></td><td><b>10.25 TL</b></td><td class="green"><b>%6.8</b></td><td>29 Eylül 2026 (Tamamlandı)</td></tr>
                <tr><td><b>FROTO</b></td><td><b>29.50 TL</b></td><td class="green"><b>%5.2</b></td><td>20 Kasım 2026</td></tr>
                <tr><td><b>BIMAS</b></td><td><b>12.00 TL</b></td><td class="green"><b>%3.8</b></td><td>18 Aralık 2026</td></tr>
                <tr><td><b>DOAS</b></td><td><b>15.40 TL</b></td><td class="green"><b>%7.5</b></td><td>15 Kasım 2026</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # TAB 7: HABER VE KAP ETKİSİ
    with tab7:
        st.subheader("🇹🇷 Günlük Haber Akışı & KAP Etki Engine")
        for n in get_daily_news():
            st.success(f"{n['title']} — ({n['category']})")

    # TAB 8: TEFAS FONLARI
    with tab8:
        st.subheader("🌐 TEFAS Fonları ve Global Piyasalar")
        st.info("TEFAS fon detayları ve döviz emtia verileri aktif şekilde sunulmaktadır.")

else:
    st.error(f"{selected_ticker} verisi alınamadı. Kod adını kontrol ediniz.")
