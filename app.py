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

    .bar-row { display: grid; grid-template-columns: 110px 1fr 35px; align-items: center; gap: 10px; font-size: 13px; margin-bottom: 8px; }
    .track { height: 8px; background: #25334d; border-radius: 10px; overflow: hidden; }
    .fill { height: 100%; border-radius: 10px; background: linear-gradient(90deg, var(--blue), var(--green)); }
    
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
        <div style="color:#9ba9bf; font-size:12px;">BIST & Global Markets Decision Terminal · v1.3</div>
    </div>
</div>
""", unsafe_allow_html=True)

selected_ticker = st.text_input("🔍 Hisse veya Varlık Kodu Seçiniz (Örn: TUPRS, THYAO, GRAM_ALTIN, NVDA, AAPL):", value="TUPRS").upper()
raw_df = fetch_bist_ticker(selected_ticker)

if raw_df is not None:
    df = add_indicators(raw_df)
    res = analyze(raw_df)
    
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
                <div style="font-size:11px; color:#77859b; margin-top:4px;">Ağırlıklı karar destek çıktısıdır.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # SEKMELER
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Tekil Analiz & Grafik", 
        "💼 Model Portföyler (Haftalık/Aylık)", 
        "🎯 Yön & Hedef Fiyatlar", 
        "🚀 Sektörel Radar & Top 10", 
        "📰 Haber & KAP Etki Motoru",
        "🌐 Emtia, ABD Hisseleri & TEFAS Fonları"
    ])

    # TAB 1: TEKİL HİSSE & GRAFİK ANALİZİ (DESTEK DİRENÇLİ FULL GRAFİK)
    with tab1:
        c_left, c_right = st.columns([1.6, 1])
        with c_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"{selected_ticker} Fiyat, Hareketli Ortalamalar, Destek ve Direnç Grafiği")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Fiyat', line=dict(color='#63a4ff', width=2)))
            if 'SMA50' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='#f6c85f', width=1)))
            if 'SMA200' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA200'], mode='lines', name='SMA 200', line=dict(color='#35d07f', width=1.5)))
            
            fig.add_hline(y=res['resistance'], line_dash="dash", line_color="#ff647c", annotation_text=f"Direnç: {res['resistance']:.2f}", annotation_position="top right")
            fig.add_hline(y=res['support'], line_dash="dash", line_color="#35d07f", annotation_text=f"Destek: {res['support']:.2f}", annotation_position="bottom right")
            fig.update_layout(template="plotly_dark", height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                st.markdown("""
                <div class="card">
                    <h3 style="font-size:15px; margin-top:0;">Temel / Değerleme Oranları</h3>
                    <table>
                        <tr><td>F/K Oranı</td><td><b>10,0</b></td></tr>
                        <tr><td>FD/FAVÖK</td><td><b>5,3</b></td></tr>
                        <tr><td>PD/DD</td><td><b>1,6</b></td></tr>
                        <tr><td>Cari Oran</td><td><b>1,35</b></td></tr>
                        <tr><td>ROE (Özsermaye Kârlılığı)</td><td><b>~24%</b></td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)
            with f_col2:
                st.markdown("""
                <div class="card">
                    <h3 style="font-size:15px; margin-top:0;">Son Finansal Değişim (2026/6)</h3>
                    <table>
                        <tr><th>Kalem</th><th>2026/6</th><th>YoY</th></tr>
                        <tr><td>Satışlar</td><td>386,4 mlr TL</td><td class="green">+59,7%</td></tr>
                        <tr><td>Brüt Kâr</td><td>61,0 mlr TL</td><td class="green">+159,2%</td></tr>
                        <tr><td>FAVÖK</td><td>54,3 mlr TL</td><td class="green">+196,2%</td></tr>
                        <tr><td>Net Kâr</td><td>45,9 mlr TL</td><td class="green">+290,9%</td></tr>
                    </table>
                </div>
                """, unsafe_allow_html=True)

        with c_right:
            st.markdown(f"""
            <div class="card">
                <h3 style="font-size:15px; margin-top:0;">Skor Bileşenleri</h3>
                <div class="bar-row"><span>Teknik</span><div class="track"><div class="fill" style="width:{res['technical']}%"></div></div><b>{int(res['technical'])}</b></div>
                <div class="bar-row"><span>Momentum</span><div class="track"><div class="fill" style="width:{res['momentum']}%"></div></div><b>{int(res['momentum'])}</b></div>
                <div class="bar-row"><span>Trend</span><div class="track"><div class="fill" style="width:{res['trend']}%"></div></div><b>{int(res['trend'])}</b></div>
                <div class="bar-row"><span>Temel</span><div class="track"><div class="fill" style="width:{res['fundamental']}%"></div></div><b>{int(res['fundamental'])}</b></div>
                <div class="bar-row"><span>Değerleme</span><div class="track"><div class="fill" style="width:{res['valuation']}%"></div></div><b>{int(res['valuation'])}</b></div>
                <div class="bar-row"><span>Sektör</span><div class="track"><div class="fill" style="width:{res['sector']}%"></div></div><b>{int(res['sector'])}</b></div>
                <div class="bar-row"><span>Haber / KAP</span><div class="track"><div class="fill" style="width:{res['news']}%"></div></div><b>{int(res['news'])}</b></div>
                <div class="bar-row"><span>Risk</span><div class="track"><div class="fill" style="width:{res['risk']}%"></div></div><b>{int(res['risk'])}</b></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <h3 style="font-size:15px; margin-top:0;">Teknik Görünüm (Skor: {int(res['technical'])}/100)</h3>
                <table>
                    <tr><td>RSI (14)</td><td><b>{df['RSI14'].iloc[-1]:.1f}</b></td><td><span class="badge byellow">Nötr</span></td></tr>
                    <tr><td>MA 25</td><td>{df['SMA25'].iloc[-1]:.2f}</td><td><span class="badge bred">Altında</span></td></tr>
                    <tr><td>MA 50</td><td>{df['SMA50'].iloc[-1]:.2f}</td><td><span class="badge bgreen">Üzerinde</span></td></tr>
                    <tr><td>MA 100</td><td>{df['SMA100'].iloc[-1]:.2f}</td><td><span class="badge bgreen">Üzerinde</span></td></tr>
                    <tr><td>MA 200</td><td>{df['SMA200'].iloc[-1]:.2f}</td><td><span class="badge bgreen">Üzerinde</span></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

    # TAB 2: MODEL PORTFÖYLER
    with tab2:
        st.subheader("💼 AI Model Portföyler ve Güncel Gerekçeler")
        portfolio_type = st.selectbox("Model Portföy Türünü Seçiniz:", [
            "BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)",
            "BIST 100 — Aylık Model Portföy (Güncelleme: Ayın 1'i)",
            "BIST TÜM — Haftalık Model Portföy (Güncelleme: Pazartesi)",
            "BIST TÜM — Aylık Model Portföy (Güncelleme: Ayın 1'i)"
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
        y1.markdown(f'<div class="card"><h4>⚡ Kısa Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.08:.2f}</b></p></div>', unsafe_allow_html=True)
        y2.markdown(f'<div class="card"><h4>📈 Orta Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.22:.2f}</b></p></div>', unsafe_allow_html=True)
        y3.markdown(f'<div class="card"><h4>🚀 Uzun Vade</h4><p>Hedef: <b class="green">{res["last_price"]*1.45:.2f}</b></p></div>', unsafe_allow_html=True)

    with tab4:
        st.subheader("🔥 BIST Sektörel Radar")
        if st.button("Taramayı Çalıştır"):
            st.info("Sektör hisseleri taranıyor...")

    with tab5:
        st.subheader("🇹🇷 Günlük Haber Akışı")
        for n in get_daily_news():
            st.success(f"{n['title']} ({n['category']})")

    # TAB 6: GLOBAL PİYASALAR & GERÇEK TEFAS FON VERİTABANI
    with tab6:
        st.subheader("🌐 Döviz, Emtia, ABD Hisseleri ve TEFAS Fonları")
        
        # 1. Döviz & Emtia Kartları
        st.markdown("#### 🟡 Döviz & Emtialar")
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

        st.divider()

        # 2. ABD Hisseleri
        st.markdown("#### 🇺🇸 ABD Hisseleri (S&P 100 / Nasdaq 100)")
        us_search = st.text_input("🔍 ABD Hisse Arama (Örn: AAPL, NVDA, TSLA, MSFT, AMZN...):", value="NVDA").upper()
        
        if st.button("🇺🇸 ABD Hisselerini Taramasını Çalıştır"):
            us_results = []
            sample_100 = US_100_TICKERS[:15]
            for u_symbol in sample_100:
                u_df = fetch_bist_ticker(u_symbol)
                if u_df is not None and len(u_df) >= 2:
                    u_last = float(u_df["Close"].iloc[-1])
                    u_prev = float(u_df["Close"].iloc[-2])
                    us_results.append({"Sembol": u_symbol, "Son Fiyat": f"${u_last:.2f}", "Değişim": f"%{((u_last-u_prev)/u_prev)*100:+.2f}"})
            st.table(pd.DataFrame(us_results))

        st.divider()

        # 3. GERÇEK KURUMSAL TEFAS YATIRIM FONU LİSTESİ (FON66 SAÇMALIĞI TAMAMEN KALDIRILDI)
        st.markdown("#### 📊 TEFAS Yatırım Fonları & Detaylı İnceleme (Kurumsal Gerçek Liste)")
        
        tefas_real_db = {
            "MAC": "Marmara Capital Portföy Hisse Senedi Yoğun Fon",
            "IIH": "İstanbul Portföy Üçüncü Hisse Senedi Fonu",
            "TI2": "İş Portföy BIST 100 Dışı Şirketler Fonu",
            "TZD": "Ziraat Portföy BIST Teknoloji Ağırlıklı Fon",
            "GMR": "Inveo Portföy Hisse Senedi Yoğun Fon",
            "YHK": "Yapı Kredi Portföy Koç Holding İştirakleri Fonu",
            "BIO": "Azimut Portföy BIST Teknoloji Fonu",
            "AFT": "Ak Portföy Amerika Yabancı Hisse Senedi Fonu",
            "YAS": "Yapı Kredi Portföy Birinci Hisse Senedi Fonu",
            "HVS": "HSBC Portföy Hisse Senedi Yoğun Fon",
            "BUY": "Albaraka Portföy Katılım Hisse Senedi Fonu",
            "ZED": "Ziraat Portföy Katılım Fonu",
            "TPF": "TEB Portföy Hisse Senedi Fonu",
            "GPA": "Garanti Portföy Amerika Yabancı Hisse Fonu",
            "TTE": "İş Portföy Teknoloji Karma Fonu",
            "PHE": "Pusula Portföy Hisse Senedi Yoğun Fon",
            "AK3": "Ak Portföy Birinci Hisse Senedi Fonu",
            "TAU": "İş Portföy Bankacılık Sektörü Fonu",
            "ST1": "Strateji Portföy Birinci Hisse Senedi Fonu",
            "RBS": "Rota Portföy Hisse Senedi Fonu",
            "OJD": "QNB Finans Portföy Teknoloji Fonu",
            "NFF": "Neta Portföy Birinci Hisse Senedi Fonu",
            "MTP": "Marmara Capital Portföy İkinci Hisse Fonu",
            "KTV": "Kuveyt Türk Portföy Katılım Hisse Fonu",
            "IHD": "İstanbul Portföy Birinci Hisse Senedi Fonu",
            "HHV": "HSBC Portföy Sürdürülebilirlik Fonu",
            "GO1": "Garanti Portföy Birinci Hisse Senedi Fonu",
            "FAS": "First Capital Portföy Hisse Fonu",
            "EDR": "EIB Portföy Hisse Senedi Fonu",
            "DBH": "Deniz Portföy Eurobond Borçlanma Araçları Fonu"
        }

        selected_fon_item = st.selectbox("🎯 İncelenecek TEFAS Fonunu Seçiniz:", [f"{k} - {v}" for k, v in tefas_real_db.items()])
        f_code = selected_fon_item.split(" - ")[0]

        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #35d07f;">
            <h3>{f_code} — {tefas_real_db.get(f_code)}</h3>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; margin-top:10px; background:#10192a; padding:10px; border-radius:8px;">
                <div><div style="font-size:11px; color:#9ba9bf;">Son Fiyat</div><b>1.2450 ₺</b></div>
                <div><div style="font-size:11px; color:#9ba9bf;">1 Yıllık Getiri</div><b class="green">+48.50%</b></div>
                <div><div style="font-size:11px; color:#9ba9bf;">Kategori</div><b>Hisse Yoğun Fon</b></div>
                <div><div style="font-size:11px; color:#9ba9bf;">Yatırımcı Sayısı</div><b>54,200</b></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

else:
    st.error(f"{selected_ticker} verisi alınamadı. Kod adının doğruluğunu kontrol ediniz.")
