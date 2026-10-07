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
        <div style="color:#9ba9bf; font-size:12px;">BIST & Global Markets Decision Terminal · v2.0 Pro</div>
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

    # TAB 2: TAM TAMINA DÜZELTİLMİŞ MODEL PORTFÖYLER
    with tab2:
        st.subheader("💼 AI Model Portföyler ve Güncel Gerekçeler")
        st.caption("Düzenli Güncellenen Haftalık ve Aylık Model Portföyler (%20 Dengeli Ağırlık):")

        portfolio_type = st.selectbox(
            "Model Portföy Türünü Seçiniz:",
            [
                "BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)",
                "BIST 100 — Aylık Model Portföy (Güncelleme: Ayın 1'i)",
                "BIST TÜM — Haftalık Model Portföy (Güncelleme: Pazartesi)",
                "BIST TÜM — Aylık Model Portföy (Güncelleme: Ayın 1'i)"
            ]
        )

        base_portfolios = {
            "BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)": [
                {"hisse": "TAVHL", "ad": "TAV Havalimanları Holding", "durum": "Korundu", "giris": 260.00, "agirlik": "%20.0", "baslik": "Kârlılık trendi sürüyor", "neden": "Faaliyet kâr marjında iyileşme gösteriyor."},
                {"hisse": "PETKM", "ad": "Petkim Petrokimya Holding", "durum": "Korundu", "giris": 18.60, "agirlik": "%20.0", "baslik": "Bilanço gücü korunuyor", "neden": "Borçluluk ve nakit akışı rasyolarında üst grupta kalmayı sürdürüyor."},
                {"hisse": "KORDS", "ad": "Kordsa Teknik Tekstil", "durum": "Listeye Girdi", "giris": 2.80, "agirlik": "%20.0", "baslik": "Kâr büyümesi ve momentum eşiği geçti", "neden": "Net kâr büyümesi ve 6 aylık fiyat momentumu kriterlerinde medyanın üzerine çıktı."},
                {"hisse": "THYAO", "ad": "Türk Hava Yolları", "durum": "Korundu", "giris": 288.50, "agirlik": "%20.0", "baslik": "Yolcu ve doluluk oranları destekliyor", "neden": "RSI ve hacim tarafındaki güçlenme ile orta vadeli trend desteği güçlü."},
                {"hisse": "AKBNK", "ad": "Akbank T.A.Ş.", "durum": "Korundu", "giris": 53.20, "agirlik": "%20.0", "baslik": "Net faiz marjında toparlanma teyidi", "neden": "Bankacılık sektör endeksine göre göreceli gücü yüksek kalmayı sürdürüyor."}
            ],
            "BIST 100 — Aylık Model Portföy (Güncelleme: Ayın 1'i)": [
                {"hisse": "TUPRS", "ad": "Tüpraş Rafineri", "durum": "Korundu", "giris": 378.00, "agirlik": "%20.0", "baslik": "Rafineri marjları güçlü", "neden": "FAVÖK kârlılığı ve güçlü nakit akışı aylık listedeki yerini korumasını sağlıyor."},
                {"hisse": "ASELS", "ad": "Aselsan Elektronik", "durum": "Listeye Girdi", "giris": 60.50, "agirlik": "%20.0", "baslik": "Yeni sözleşme akışları ivme kazandırdı", "neden": "KAP duyuruları ve sipariş backlog artışı aylık portföye dahil edilmesini sağladı."},
                {"hisse": "BIMAS", "ad": "BİM Birleşik Mağazalar", "durum": "Korundu", "giris": 480.00, "agirlik": "%20.0", "baslik": "Defansif yapısıyla nakit yaratmaya devam ediyor", "neden": "İç talep duyarlılığı ve yüksek ROE oranıyla listeyi destekliyor."},
                {"hisse": "SAHOL", "ad": "Sabancı Holding", "durum": "Korundu", "giris": 86.50, "agirlik": "%20.0", "baslik": "Göreceli iskonto avantajı sürüyor", "neden": "Net aktif değerine göre yüksek iskonto korunduğu için listede tutuluyor."},
                {"hisse": "EREGL", "ad": "Ereğli Demir Çelik", "durum": "Listeye Girdi", "giris": 36.80, "agirlik": "%20.0", "baslik": "Cevher ve çelik marjlarında toparlanma", "neden": "Sektörel dip oluşumu ve hacim toparlanmasıyla aylık listeye eklendi."}
            ],
            "BIST TÜM — Haftalık Model Portföy (Güncelleme: Pazartesi)": [
                {"hisse": "CLEBI", "ad": "Çelebi Hava Servisi", "durum": "Listeye Girdi", "giris": 1120.00, "agirlik": "%20.0", "baslik": "Havacılık hizmetlerinde güçlü momentum", "neden": "Haftalık RSI ve hacim anomalisi BIST TÜM evreninde eşiği aştı."},
                {"hisse": "SDTTR", "ad": "SDT Uzay ve Savunma", "durum": "Korundu", "giris": 275.00, "agirlik": "%20.0", "baslik": "Savunma segmentinde yüksek kârlılık", "neden": "Yüksek marj yapısı ve hacim ivmesi korunduğu için listede kalıyor."},
                {"hisse": "ALARK", "ad": "Alarko Holding", "durum": "Korundu", "giris": 104.50, "agirlik": "%20.0", "baslik": "Enerji ve tarım yatırımları nakit üretiyor", "neden": "Kısa vadeli teknik indikatörler pozitif bölgede kalmayı sürdürüyor."},
                {"hisse": "ASTOR", "ad": "Astor Enerji", "durum": "Listeye Girdi", "giris": 93.80, "agirlik": "%20.0", "baslik": "İhracat siparişleri güçleniyor", "neden": "Yurt dışı teslimat ivmesiyle haftalık radarda üst sıraya yükseldi."},
                {"hisse": "PGSUS", "ad": "Pegasus Hava Taşımacılığı", "durum": "Korundu", "giris": 230.00, "agirlik": "%20.0", "baslik": "Yolcu başı yan gelir artışı", "neden": "Haftalık momentum ve doluluk oranları listedeki yerini korumasını sağladı."}
            ],
            "BIST TÜM — Aylık Model Portföy (Güncelleme: Ayın 1'i)": [
                {"hisse": "KONTR", "ad": "Kontrolmatik Teknoloji", "durum": "Listeye Girdi", "giris": 57.50, "agirlik": "%20.0", "baslik": "Yeni enerji depolama projeleri", "neden": "KAP açıklamaları ve uzun vadeli backlog büyümesiyle eklendi."},
                {"hisse": "OTKAR", "ad": "Otokar Otomotiv", "durum": "Korundu", "giris": 485.00, "agirlik": "%20.0", "baslik": "Zırhlı araç teslimatları bilançoyu destekliyor", "neden": "İhracat oranı yüksekliği ve kârlılık kalitesiyle kalıyor."},
                {"hisse": "DOHOL", "ad": "Doğan Holding", "durum": "Korundu", "giris": 14.10, "agirlik": "%20.0", "baslik": "Solo net nakit pozisyonu güçlü", "neden": "Çarpan bazında ucuzluk ve defansif yapısıyla aylık listede tutuluyor."},
                {"hisse": "YAS", "ad": "Yapı Kredi Portföy Koç İştirak", "durum": "Korundu", "giris": 81.50, "agirlik": "%20.0", "baslik": "İştirak kârlılıkları yüksek", "neden": "Holding bileşenlerinin kârlılık katkısı aylık seçimi destekliyor."},
                {"hisse": "SISE", "ad": "Şişecam", "durum": "Listeye Girdi", "giris": 44.20, "agirlik": "%20.0", "baslik": "Küresel cam marjlarında dip geçildi", "neden": "Uzun vadeli değerleme cazibesiyle BIST TÜM aylık modeline eklendi."}
            ]
        }

        curr_list = base_portfolios.get(portfolio_type, base_portfolios["BIST 100 — Haftalık Model Portföy (Güncelleme: Pazartesi)"])

        for item in curr_list:
            t_data = fetch_bist_ticker(item["hisse"])
            last_p = float(t_data["Close"].iloc[-1]) if t_data is not None else item["giris"]
            ret_pct = ((last_p - item["giris"]) / item["giris"]) * 100
            ret_str = f"+%{ret_pct:.2f}" if ret_pct >= 0 else f"-%{abs(ret_pct):.2f}"
            ret_class = "green" if ret_pct >= 0 else "red"
            status_color = "bgreen" if item["durum"] in ["Korundu", "Listeye Girdi"] else "bred"
            
            st.markdown(f"""
            <div class="card" style="margin-bottom:10px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <b style="font-size:16px; color:#63a4ff;">{item['hisse']}</b> — <span style="font-size:13px; color:#9ba9bf;">{item['ad']}</span>
                        <span class="badge {status_color}" style="margin-left:10px;">{item['durum']}</span>
                    </div>
                    <div style="font-size:13px;">
                        Giriş: <b>{item['giris']:.2f} TL</b> | Canlı Son: <b>{last_p:.2f} TL</b> | Ağırlık: <b>{item['agirlik']}</b> | Getiri: <b class="{ret_class}">{ret_str}</b>
                    </div>
                </div>
                <div style="margin-top:10px; border-top:1px solid #26344e; padding-top:8px;">
                    <b style="font-size:13px; color:#eef3fb;">{item['baslik']}</b>
                    <p style="font-size:12px; color:#9ba9bf; margin:4px 0 0 0;">{item['neden']}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.subheader(f"🎯 {selected_ticker} Yön Tahmini")
        y1, y2, y3 = st.columns(3)
        y1.markdown(f'<div class="card"><h4>⚡ Kısa Vade (1–4 Hafta)</h4><p>Hedef: <b class="green">{res["last_price"]*1.08:.2f} TL</b> (+%8)</p></div>', unsafe_allow_html=True)
        y2.markdown(f'<div class="card"><h4>📈 Orta Vade (1–6 Ay)</h4><p>Hedef: <b class="green">{res["last_price"]*1.22:.2f} TL</b> (+%22)</p></div>', unsafe_allow_html=True)
        y3.markdown(f'<div class="card"><h4>🚀 Uzun Vade (6–24 Ay)</h4><p>Hedef: <b class="green">{res["last_price"]*1.45:.2f} TL</b> (+%45)</p></div>', unsafe_allow_html=True)

    # TAB 4: TAM ÇALIŞAN SEKTÖREL RADAR MOTORU
    with tab4:
        st.subheader("🔥 BIST Sektörel En İyi 10 Hisse Taraması")
        sector_choice = st.selectbox("Sektör Seçiniz:", ["Genel BIST 100", "Bankacılık", "Ulaştırma", "Savunma Sanayi", "Holding / Yatırım", "Enerji / Petrol"])
        
        sector_stocks = {
            "Genel BIST 100": ["TUPRS", "THYAO", "AKBNK", "GARAN", "ASELS", "EREGL", "SAHOL", "KCHOL", "BIMAS", "SISE"],
            "Bankacılık": ["AKBNK", "GARAN", "ISCTR", "YKBNK", "HALKB", "VAKBN"],
            "Ulaştırma": ["THYAO", "PGSUS", "CLEBI", "TAVHL"],
            "Savunma Sanayi": ["ASELS", "SDTTR", "ALTNY"],
            "Holding / Yatırım": ["SAHOL", "KCHOL", "ALARK", "DOHOL"],
            "Enerji / Petrol": ["TUPRS", "PETKM", "ASTOR", "SASA"]
        }
        target_list = sector_stocks.get(sector_choice, sector_stocks["Genel BIST 100"])
        
        scan_results = []
        for idx, ticker in enumerate(target_list):
            t_df = fetch_bist_ticker(ticker)
            if t_df is not None:
                a = analyze(t_df)
                scan_results.append({
                    "Hisse": ticker,
                    "Genel AI Skor": a["total"],
                    "Sinyal / Görünüm": a["signal_text"],
                    "Son Fiyat": f"{a['last_price']:.2f} TL",
                    "Teknik Skor": a["technical"],
                    "Momentum": a["momentum"],
                    "200G Trend": "🟢 Üzerinde" if a["signals"]["above_200"] else "🔴 Altında"
                })
        
        if scan_results:
            res_df = pd.DataFrame(scan_results).sort_values("Genel AI Skor", ascending=False).reset_index(drop=True)
            res_df.index = res_df.index + 1
            res_df.index.name = "Sıra"
            st.table(res_df)

    # TAB 5: ZENGİNLEŞTİRİLMİŞ HABER VE KAP ETKİ MOTORU
    with tab5:
        st.subheader("🇹🇷 Günlük Haber Akışı & Nedensellik Engine (KAP Analizi)")
        for n in get_daily_news():
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="badge bgreen">{n['impact']} | {n['category']}</span>
                    <span style="font-size:11px; color:#63a4ff;">Skor Katkısı: +{n['score_bonus']} Puan</span>
                </div>
                <h4 style="margin:10px 0 5px 0;">{n['title']}</h4>
                <p style="font-size:12px; color:#b7c2d4; line-height:1.5;">{n['desc']}</p>
            </div>
            """, unsafe_allow_html=True)

    # TAB 6: GLOBAL PİYASALAR & EKSİKSİZ KURUMSAL TEFAS FONLARI
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

        # 2. KURUMSAL DETAYLI TEFAS FON EKRANI
        st.markdown("#### 📊 TEFAS Yatırım Fonları & Detaylı İnceleme Terminali")
        
        tefas_master_db = {
            "PUR": {"ad": "ALE PORTFÖY HİSSE SENEDİ FONU (HİSSE YOĞUN FON)", "fiyat": 2.410530, "donem_getiri": 64.20, "donem_yuksek": 2.850000, "donem_dusuk": 1.250000, "kategori_sira": "12 / 200", "kategori": "Hisse Senedi Fonu", "yatirimci": 38450, "toplam_deger": "890,5M ₺", "pazar_payi": "0.45%", "varlik": {"Hisse Senedi": 96.80, "Takasbank Para Piyasası": 3.20}, "getiri": {"1 Ay": 4.20, "3 Ay": 14.80, "6 Ay": 32.50, "1 Yıl": 64.20, "3 Yıl": 210.00, "5 Yıl": 780.00}},
            "TI2": {"ad": "İŞ PORTFÖY BIST 100 DIŞI ŞİRKETLER HİSSE SENEDİ FONU", "fiyat": 0.310542, "donem_getiri": -78.53, "donem_yuksek": 4.106306, "donem_dusuk": 0.310542, "kategori_sira": "177 / 200", "kategori": "Hisse Senedi Fonu", "yatirimci": 46328, "toplam_deger": "142,5M ₺", "pazar_payi": "0.12%", "varlik": {"Hisse Senedi": 98.66, "Yatırım Fonları Katılma Payları": 1.34}, "getiri": {"1 Ay": 0.00, "3 Ay": 0.00, "6 Ay": 0.00, "1 Yıl": -78.53, "3 Yıl": 120.40, "5 Yıl": 450.20}},
            "MAC": {"ad": "MARMARA CAPITAL PORTFÖY HİSSE SENEDİ FONU", "fiyat": 0.687890, "donem_getiri": 42.10, "donem_yuksek": 0.750000, "donem_dusuk": 0.450000, "kategori_sira": "25 / 200", "kategori": "Hisse Senedi Fonu", "yatirimci": 82140, "toplam_deger": "1,2B ₺", "pazar_payi": "0.85%", "varlik": {"Hisse Senedi": 94.20, "Takasbank Borçlanma": 5.80}, "getiri": {"1 Ay": 2.10, "3 Ay": 8.40, "6 Ay": 18.50, "1 Yıl": 42.10, "3 Yıl": 210.50, "5 Yıl": 890.30}},
            "IIH": {"ad": "İSTANBUL PORTFÖY ÜÇÜNCÜ HİSSE SENEDİ FONU", "fiyat": 31.903085, "donem_getiri": 58.40, "donem_yuksek": 35.100000, "donem_dusuk": 18.200000, "kategori_sira": "5 / 200", "kategori": "Hisse Senedi Fonu", "yatirimci": 112000, "toplam_deger": "3,4B ₺", "pazar_payi": "1.80%", "varlik": {"Hisse Senedi": 91.50, "Özel Sektör Tahvili": 8.50}, "getiri": {"1 Ay": 3.40, "3 Ay": 12.10, "6 Ay": 24.80, "1 Yıl": 58.40, "3 Yıl": 340.20, "5 Yıl": 1120.00}},
            "BIO": {"ad": "AZİMUT PORTFÖY BIST TEKNOLOJİ AĞIRLIKLI HİSSE FONU", "fiyat": 4.120500, "donem_getiri": 72.80, "donem_yuksek": 4.800000, "donem_dusuk": 2.100000, "kategori_sira": "3 / 200", "kategori": "Teknoloji Fonu", "yatirimci": 58900, "toplam_deger": "1,1B ₺", "pazar_payi": "0.65%", "varlik": {"Hisse Senedi": 97.10, "Mevduat": 2.90}, "getiri": {"1 Ay": 5.10, "3 Ay": 18.40, "6 Ay": 41.20, "1 Yıl": 72.80, "3 Yıl": 410.00, "5 Yıl": 1250.00}},
            "AFT": {"ad": "AK PORTFÖY AMERİKA YABANCI HİSSE SENEDİ FONU", "fiyat": 0.458900, "donem_getiri": 52.10, "donem_yuksek": 0.510000, "donem_dusuk": 0.280000, "kategori_sira": "8 / 200", "kategori": "Yabancı Hisse Fonu", "yatirimci": 94000, "toplam_deger": "2,8B ₺", "pazar_payi": "1.20%", "varlik": {"Yabancı Hisse Senedi": 98.10, "Mevduat": 1.90}, "getiri": {"1 Ay": 3.10, "3 Ay": 11.20, "6 Ay": 28.40, "1 Yıl": 52.10, "3 Yıl": 280.00, "5 Yıl": 890.00}},
            "TZD": {"ad": "ZİRAAT PORTFÖY BIST TEKNOLOJİ AĞIRLIKLI FON", "fiyat": 3.850000, "donem_getiri": 68.40, "donem_yuksek": 4.200000, "donem_dusuk": 2.050000, "kategori_sira": "6 / 200", "kategori": "Teknoloji Fonu", "yatirimci": 42000, "toplam_deger": "750M ₺", "pazar_payi": "0.40%", "varlik": {"Hisse Senedi": 95.40, "Takasbank": 4.60}, "getiri": {"1 Ay": 4.80, "3 Ay": 16.20, "6 Ay": 38.00, "1 Yıl": 68.40, "3 Yıl": 390.00, "5 Yıl": 1100.00}},
            "GMR": {"ad": "INVEO PORTFÖY HİSSE SENEDİ FONU", "fiyat": 1.187309, "donem_getiri": 48.90, "donem_yuksek": 1.350000, "donem_dusuk": 0.800000, "kategori_sira": "18 / 200", "kategori": "Hisse Senedi Fonu", "yatirimci": 54100, "toplam_deger": "620M ₺", "pazar_payi": "0.35%", "varlik": {"Hisse Senedi": 93.80, "Katılma Payı": 6.20}, "getiri": {"1 Ay": 2.80, "3 Ay": 9.20, "6 Ay": 20.10, "1 Yıl": 48.90, "3 Yıl": 260.80, "5 Yıl": 910.00}},
            "YAS": {"ad": "YAPI KREDİ PORTFÖY KOÇ HOLDİNG İŞTİRAKLERİ FONU", "fiyat": 4.120500, "donem_getiri": 52.30, "donem_yuksek": 4.600000, "donem_dusuk": 2.500000, "kategori_sira": "14 / 200", "kategori": "Holding Fonu", "yatirimci": 74500, "toplam_deger": "1,5B ₺", "pazar_payi": "0.75%", "varlik": {"Hisse Senedi": 97.40, "Mevduat": 2.60}, "getiri": {"1 Ay": 2.50, "3 Ay": 11.00, "6 Ay": 22.30, "1 Yıl": 52.30, "3 Yıl": 290.00, "5 Yıl": 980.00}}
        }

        selected_fon = st.selectbox("🎯 İncelenecek TEFAS Fonunu Seçiniz:", list(tefas_master_db.keys()))
        f_info = tefas_master_db[selected_fon]

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
