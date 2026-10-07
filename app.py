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
        <div style="color:#9ba9bf; font-size:12px;">BIST & Global Markets Decision Terminal · v1.8</div>
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
    p_lev = res["p_levels"]
    
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
        "📊 Tekil Analiz & AI Yorumu", 
        "💼 Model Portföyler (Haftalık/Aylık)", 
        "🎯 Yön & Hedef Fiyatlar", 
        "🚀 Sektörel Radar & Top 10", 
        "📰 Haber & KAP Etki Motoru",
        "🌐 Emtia, ABD Hisseleri & TEFAS Fonları"
    ])

    # TAB 1: TEKİL HİSSE ANALİZİ
    with tab1:
        c_left, c_right = st.columns([1.6, 1])
        with c_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"{selected_ticker} Fiyat, Majör Destek & Direnç Grafiği")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Fiyat', line=dict(color='#63a4ff', width=2)))
            if 'SMA50' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='#f6c85f', width=1)))
            if 'SMA200' in df:
                fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA200'], mode='lines', name='SMA 200', line=dict(color='#35d07f', width=1.5)))
            
            fig.add_hline(y=p_lev['R2'], line_dash="dash", line_color="#ff4d4d", annotation_text=f"2. Ana Direnç R2: {p_lev['R2']}", annotation_position="top right")
            fig.add_hline(y=p_lev['R1'], line_dash="dash", line_color="#ff9999", annotation_text=f"1. Ara Direnç R1: {p_lev['R1']}", annotation_position="top right")
            fig.add_hline(y=p_lev['S1'], line_dash="dash", line_color="#80ff80", annotation_text=f"1. Ara Destek S1: {p_lev['S1']}", annotation_position="bottom right")
            fig.add_hline(y=p_lev['S2'], line_dash="dash", line_color="#35d07f", annotation_text=f"2. Ana Destek S2: {p_lev['S2']}", annotation_position="bottom right")
            
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
                <h3 style="font-size:15px; margin-top:0;">Geniş Marjlı Destek & Dirençler</h3>
                <table>
                    <tr><td>2. Ana Direnç (R2)</td><td><b class="red">{p_lev['R2']} TL</b></td></tr>
                    <tr><td>1. Ara Direnç (R1)</td><td><b class="red">{p_lev['R1']} TL</b></td></tr>
                    <tr><td>Mevcut Fiyat</td><td><b class="yellow">{res['last_price']:.2f} TL</b></td></tr>
                    <tr><td>1. Ara Destek (S1)</td><td><b class="green">{p_lev['S1']} TL</b></td></tr>
                    <tr><td>2. Ana Destek (S2)</td><td><b class="green">{p_lev['S2']} TL</b></td></tr>
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

    # TAB 6: GLOBAL PİYASALAR & SELCOIN BİREBİR DETAYLI TEFAS FON EKRANI
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

        st.markdown("**📈 Canlı Grafik İnceleme Kısayolları (Tıkla ve Tekil Analizde Grafik Aç):**")
        b_col1, b_col2, b_col3, b_col4, b_col5, b_col6 = st.columns(6)
        
        if b_col1.button("Gram Altın 📊"):
            st.session_state["selected_ticker"] = "GRAM_ALTIN"
            st.rerun()
        if b_col2.button("Ons Altın 🪙"):
            st.session_state["selected_ticker"] = "ONS_ALTIN"
            st.rerun()
        if b_col3.button("Gram Gümüş 🥈"):
            st.session_state["selected_ticker"] = "GRAM_GUMUS"
            st.rerun()
        if b_col4.button("Ons Gümüş 💎"):
            st.session_state["selected_ticker"] = "ONS_GUMUS"
            st.rerun()
        if b_col5.button("Brent Petrol 🛢️"):
            st.session_state["selected_ticker"] = "PETROL"
            st.rerun()
        if b_col6.button("Dolar/TL 💵"):
            st.session_state["selected_ticker"] = "USDTRY"
            st.rerun()

        st.divider()

        # 2. SELCOIN BİREBİR DETAYLI TEFAS FON DETAY EKRANI (PUR, TI2, MAC vb.)
        st.markdown("#### 📊 TEFAS Yatırım Fonları & Detaylı İnceleme (Selcoin Model)")
        
        # Selcoin Tarzı Zengin Detaylı TEFAS Veritabanı
        tefas_selcoin_db = {
            "PUR": {
                "ad": "ALE PORTFÖY HİSSE SENEDİ FONU (HİSSE SENEDİ YOĞUN FON)",
                "fiyat": 2.410530,
                "donem_getiri": 64.20,
                "donem_yuksek": 2.850000,
                "donem_dusuk": 1.250000,
                "kategori_sira": "12 / 200",
                "kategori": "Hisse Senedi Fonu",
                "yatirimci": 38450,
                "toplam_deger": "890,5M ₺",
                "pazar_payi": "0.45%",
                "varlik": {"Hisse Senedi": 96.80, "Takasbank Para Piyasası": 3.20},
                "getiri": {"1 Ay": 4.20, "3 Ay": 14.80, "6 Ay": 32.50, "1 Yıl": 64.20, "3 Yıl": 210.00, "5 Yıl": 780.00}
            },
            "TI2": {
                "ad": "İŞ PORTFÖY BIST 100 DIŞI ŞİRKETLER HİSSE SENEDİ FONU",
                "fiyat": 0.310542,
                "donem_getiri": -78.53,
                "donem_yuksek": 4.106306,
                "donem_dusuk": 0.310542,
                "kategori_sira": "177 / 200",
                "kategori": "Hisse Senedi Fonu",
                "yatirimci": 46328,
                "toplam_deger": "142,5M ₺",
                "pazar_payi": "0.12%",
                "varlik": {"Hisse Senedi": 98.66, "Yatırım Fonları Katılma Payları": 1.34},
                "getiri": {"1 Ay": 0.00, "3 Ay": 0.00, "6 Ay": 0.00, "1 Yıl": -78.53, "3 Yıl": 120.40, "5 Yıl": 450.20}
            },
            "MAC": {
                "ad": "MARMARA CAPITAL PORTFÖY HİSSE SENEDİ FONU",
                "fiyat": 0.687890,
                "donem_getiri": 42.10,
                "donem_yuksek": 0.750000,
                "donem_dusuk": 0.450000,
                "kategori_sira": "25 / 200",
                "kategori": "Hisse Senedi Fonu",
                "yatirimci": 82140,
                "toplam_deger": "1,2B ₺",
                "pazar_payi": "0.85%",
                "varlik": {"Hisse Senedi": 94.20, "Takasbank Borçlanma": 5.80},
                "getiri": {"1 Ay": 2.10, "3 Ay": 8.40, "6 Ay": 18.50, "1 Yıl": 42.10, "3 Yıl": 210.50, "5 Yıl": 890.30}
            },
            "IIH": {
                "ad": "İSTANBUL PORTFÖY ÜÇÜNCÜ HİSSE SENEDİ FONU",
                "fiyat": 31.903085,
                "donem_getiri": 58.40,
                "donem_yuksek": 35.100000,
                "donem_dusuk": 18.200000,
                "kategori_sira": "5 / 200",
                "kategori": "Hisse Senedi Fonu",
                "yatirimci": 112000,
                "toplam_deger": "3,4B ₺",
                "pazar_payi": "1.80%",
                "varlik": {"Hisse Senedi": 91.50, "Özel Sektör Tahvili": 8.50},
                "getiri": {"1 Ay": 3.40, "3 Ay": 12.10, "6 Ay": 24.80, "1 Yıl": 58.40, "3 Yıl": 340.20, "5 Yıl": 1120.00}
            },
            "BIO": {
                "ad": "AZİMUT PORTFÖY BIST TEKNOLOJİ AĞIRLIKLI HİSSE FONU",
                "fiyat": 4.120500,
                "donem_getiri": 72.80,
                "donem_yuksek": 4.800000,
                "donem_dusuk": 2.100000,
                "kategori_sira": "3 / 200",
                "kategori": "Teknoloji Fonu",
                "yatirimci": 58900,
                "toplam_deger": "1,1B ₺",
                "pazar_payi": "0.65%",
                "varlik": {"Hisse Senedi": 97.10, "Mevduat": 2.90},
                "getiri": {"1 Ay": 5.10, "3 Ay": 18.40, "6 Ay": 41.20, "1 Yıl": 72.80, "3 Yıl": 410.00, "5 Yıl": 1250.00}
            }
        }

        selected_fon = st.selectbox("🎯 İncelenecek TEFAS Fonunu Seçiniz (PUR, TI2, MAC, IIH, BIO...):", list(tefas_selcoin_db.keys()))
        f_info = tefas_selcoin_db[selected_fon]

        # SELCOIN BİREBİR ÜST BAŞLIK KARTI
        st.markdown(f"""
        <div class="card" style="border-left: 4px solid #63a4ff;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="badge bgreen">{selected_fon}</span> <span style="font-size:11px; color:#9ba9bf;">TEFAS FON FİYAT GEÇMİŞİ</span>
                    <h2 style="margin:6px 0 0 0; font-size:20px;">{f_info['ad']}</h2>
                </div>
            </div>
            <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:15px; margin-top:15px; background:#10192a; padding:12px; border-radius:10px;">
                <div>
                    <div style="font-size:11px; color:#9ba9bf;">Son Fiyat</div>
                    <div style="font-size:18px; font-weight:800;">{f_info['fiyat']:.6f} ₺</div>
                </div>
                <div>
                    <div style="font-size:11px; color:#9ba9bf;">Dönem Getirisi</div>
                    <div class="{'green' if f_info['donem_getiri'] >= 0 else 'red'}" style="font-size:18px; font-weight:800;">%{f_info['donem_getiri']:+.2f}</div>
                </div>
                <div>
                    <div style="font-size:11px; color:#9ba9bf;">Dönem En Yüksek</div>
                    <div style="font-size:18px; font-weight:800;">{f_info['donem_yuksek']:.6f} ₺</div>
                </div>
                <div>
                    <div style="font-size:11px; color:#9ba9bf;">Dönem En Düşük</div>
                    <div style="font-size:18px; font-weight:800;">{f_info['donem_dusuk']:.6f} ₺</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ÜÇLÜ BİLGİ BLOĞU (FON BİLGİSİ - VARLIK DAĞILIMI - GETİRİ BİLGİSİ)
        fb_col1, fb_col2, fb_col3 = st.columns(3)

        with fb_col1:
            st.markdown(f"""
            <div class="card">
                <h4 style="margin-top:0;">Fon Bilgisi 💰</h4>
                <table>
                    <tr><td>Son Fiyat (TL)</td><td><b>{f_info['fiyat']:.6f} ₺</b></td></tr>
                    <tr><td>Kategori</td><td><b>{f_info['kategori']}</b></td></tr>
                    <tr><td>Kategori Derecesi</td><td><b>{f_info['kategori_sira']}</b></td></tr>
                    <tr><td>Yatırımcı Sayısı</td><td><b>{f_info['yatirimci']:,}</b></td></tr>
                    <tr><td>Fon Toplam Değer</td><td><b>{f_info['toplam_deger']}</b></td></tr>
                    <tr><td>Pazar Payı</td><td><b>{f_info['pazar_payi']}</b></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

        with fb_col2:
            st.markdown("""
            <div class="card">
                <h4 style="margin-top:0;">Fon Varlık Dağılımı 📊</h4>
                <table>
                    <tr><th>Varlık Türü</th><th>Oran (%)</th></tr>
            """, unsafe_allow_html=True)
            for v_tur, v_oran in f_info["varlik"].items():
                st.markdown(f"<tr><td>{v_tur}</td><td><b>%{v_oran:.2f}</b></td></tr>", unsafe_allow_html=True)
            st.markdown("</table></div>", unsafe_allow_html=True)

        with fb_col3:
            st.markdown("""
            <div class="card">
                <h4 style="margin-top:0;">Getiri Bilgisi 📈</h4>
                <table>
                    <tr><th>Dönem</th><th>Getiri (%)</th></tr>
            """, unsafe_allow_html=True)
            for g_donem, g_oran in f_info["getiri"].items():
                g_clr = "green" if g_oran >= 0 else "red"
                st.markdown(f"<tr><td>Son {g_donem} Getirisi</td><td class='{g_clr}'><b>%{g_oran:+.2f}</b></td></tr>", unsafe_allow_html=True)
            st.markdown("</table></div>", unsafe_allow_html=True)

else:
    st.error(f"{selected_ticker} verisi alınamadı. Kod adının doğruluğunu kontrol ediniz.")
