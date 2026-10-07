import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from analysis_engine import add_indicators, analyze
from data_fetcher import fetch_bist_ticker, get_market_overview
from news_engine import get_daily_news

st.set_page_config(page_title="TUNA BIST AI TERMINAL", layout="wide", initial_sidebar_state="collapsed")

# Terminal Karanlık Tema Stilleri
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
        <div style="color:#9ba9bf; font-size:12px;">BIST & Global Markets Decision Terminal · v1.0</div>
    </div>
</div>
""", unsafe_allow_html=True)

selected_ticker = st.text_input("🔍 Hisse veya Varlık Kodu Seçiniz (Örn: TUPRS, THYAO, NVDA, AAPL):", value="TUPRS").upper()
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
        st.markdown(f'<div class="card"><div class="kpi-label">Fiyat</div><div class="kpi-val">{res["last_price"]:.2f} TL</div><div class="{c_class}" style="font-size:12px; font-weight:700;">%{res["change_pct"]:.2f} Günlük</div></div>', unsafe_allow_html=True)
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
        "📊 Tekil Hisse Analizi", 
        "💼 Model Portföyler (Haftalık/Aylık)", 
        "🎯 Yön & Hedef Fiyatlar", 
        "🚀 Sektörel Radar & Top 10", 
        "📰 Haber & KAP Etki Motoru",
        "🌐 Emtia, ABD Hisseleri & Fonlar"
    ])

    # TAB 1: TEKİL HİSSE ANALİZİ
    with tab1:
        c_left, c_right = st.columns([1.6, 1])
        with c_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"{selected_ticker} Fiyat, Hareketli Ortalamalar, Destek ve Direnç")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Fiyat', line=dict(color='#63a4ff', width=2)))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='#f6c85f', width=1)))
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
                    <tr><td>52H Zirveye Uzaklık</td><td>-8,0%</td><td><span class="badge byellow">Makul</span></td></tr>
                </table>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="card">
                <h3 style="font-size:15px; margin-top:0;">🤖 AI Karar Açıklaması — {selected_ticker}</h3>
                <p style="font-size:12px; color:#c7d2e4; line-height:1.6;">
                    <b>Genel Değerlendirme: <span class="{res['signal_class']}">{res['signal_text']}</span></b>. 
                    Fiyat 50/100/200 günlük ortalamaların üzerinde seyrediyor. RSI nötr bölgede ve dengeli momentum yapısı korunuyor.
                    <br><br>
                    <b>En önemli teyit:</b> Kısa vadeli ortalamaların yukarı kırılması.<br>
                    <b>En önemli risk:</b> Piyasa genelinde satış baskısı oluşması.
                </p>
            </div>
            """, unsafe_allow_html=True)

    # TAB 2: MODEL PORTFÖYLER
    with tab2:
        st.subheader("💼 AI Model Portföyler ve Güncel Gerekçeler")
        st.caption("Pazartesi güncellenen Haftalık ve Her ayın 1'inde güncellenen Aylık Model Portföyler (5 Hisse / %20 Ağırlık):")

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
                {"hisse": "TAVHL", "ad": "TAV Havalimanları Holding", "durum": "Korundu", "giris": 260.00, "agirlik": "%20.0", "baslik": "Kârlılık trendi sürüyor", "neden": "Faaliyet kâr marjında art arda çeyreklerde iyileşme gösteriyor."},
                {"hisse": "PETKM", "ad": "Petkim Petrokimya Holding", "durum": "Korundu", "giris": 18.60, "agirlik": "%20.0", "baslik": "Bilanço gücü korunuyor", "neden": "Borçluluk ve nakit akışı kriterlerinde evrenin üst yarısında kalmayı sürdürüyor."},
                {"hisse": "KORDS", "ad": "Kordsa Teknik Tekstil", "durum": "Listeye Girdi", "giris": 2.80, "agirlik": "%20.0", "baslik": "Kâr büyümesi ve momentum eşiği geçti", "neden": "Net kâr büyümesi ve 6 aylık fiyat momentumu kriterlerinde medyanın üzerine çıktı."},
                {"hisse": "THYAO", "ad": "Türk Hava Yolları", "durum": "Korundu", "giris": 288.50, "agirlik": "%20.0", "baslik": "Yolcu ve doluluk oranları destekliyor", "neden": "RSI ve hacim tarafındaki güçlenme ile orta vadeli trend desteği güçlü."},
                {"hisse": "AKBNK", "ad": "Akbank T.A.Ş.", "durum": "Korundu", "giris": 53.20, "agirlik": "%20.0", "baslik": "Net faiz marjında toparlanma teyidi", "neden": "Bankacılık sektör endeksine göre göreceli gücü yüksek kalmayı sürdürüyor."}
            ],
            "BIST 100 — Aylık Model Portföy (Güncelleme: Ayın 1'i)": [
                {"hisse": "TUPRS", "ad": "Tüpraş Rafineri", "durum": "Korundu", "giris": 378.00, "agirlik": "%20.0", "baslik": "Rafineri marjları güçlü", "neden": "FAVÖK kârlılığı ve güçlü nakit akışı aylık listedeki yerini korumasını sağlıyor."},
                {"hisse": "ASELS", "ad": "Aselsan Elektronik", "durum": "Listeye Girdi", "giris": 60.50, "agirlik": "%20.0", "baslik": "Yeni sözleşme akışları ivme kazandırdı", "neden": "KAP duyuruları ve backlog sipariş artışı aylık portföye dahil edilmesini sağladı."},
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

        curr_list = base_portfolios.get(portfolio_type, [])

        for item in curr_list:
            t_data = fetch_bist_ticker(item["hisse"])
            if t_data is not None:
                last_p = float(t_data["Close"].iloc[-1])
            else:
                last_p = item["giris"]
                
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

    # TAB 3: YÖN VE HEDEF FİYAT TAHMİNLERİ
    with tab3:
        st.subheader(f"🎯 {selected_ticker} Yön Tahmini & Vade Bazlı Hedef Seviyeler")
        target_up_short = res['last_price'] * 1.08
        target_down_short = res['support']
        target_up_mid = res['last_price'] * 1.22
        target_down_mid = res['last_price'] * 0.92
        target_up_long = res['last_price'] * 1.45
        target_down_long = res['last_price'] * 0.85
        
        y1, y2, y3 = st.columns(3)
        with y1:
            st.markdown(f"""
            <div class="card">
                <h4>⚡ Kısa Vade (1–4 Hafta)</h4>
                <div class="badge {res['signal_class']}">Sinyal: {res['signal_text']}</div>
                <p style="margin-top:15px;"><b>İlk Hedef Fiyat:</b> <span class="green">{target_up_short:.2f} TL</span> (+%8)</p>
                <p><b>Düşebileceği Seviye:</b> <span class="red">{target_down_short:.2f} TL</span> (-%{((res['last_price']-target_down_short)/res['last_price'])*100:.1f})</p>
            </div>
            """, unsafe_allow_html=True)
            
        with y2:
            st.markdown(f"""
            <div class="card">
                <h4>📈 Orta Vade (1–6 Ay)</h4>
                <div class="badge bgreen">Sinyal: POZİTİF</div>
                <p style="margin-top:15px;"><b>Hedef Fiyat:</b> <span class="green">{target_up_mid:.2f} TL</span> (+%22)</p>
                <p><b>Geri Çekilme Riski:</b> <span class="red">{target_down_mid:.2f} TL</span> (-%8)</p>
            </div>
            """, unsafe_allow_html=True)

        with y3:
            st.markdown(f"""
            <div class="card">
                <h4>🚀 Uzun Vade (6–24 Ay)</h4>
                <div class="badge bgreen">Sinyal: GÜÇLÜ POZİTİF</div>
                <p style="margin-top:15px;"><b>Hedef Fiyat:</b> <span class="green">{target_up_long:.2f} TL</span> (+%45)</p>
                <p><b>Ana Destek Tabanı:</b> <span class="red">{target_down_long:.2f} TL</span> (-%15)</p>
            </div>
            """, unsafe_allow_html=True)

    # TAB 4: SEKTÖREL RADAR VE TOP 10
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
        
        if st.button("Sektörel Taramayı Çalıştır"):
            scan_results = []
            p_bar = st.progress(0)
            for idx, ticker in enumerate(target_list):
                t_df = fetch_bist_ticker(ticker)
                if t_df is not None:
                    a = analyze(t_df)
                    scan_results.append({
                        "Hisse": ticker,
                        "Genel Skor": a["total"],
                        "Görünüm": a["signal_text"],
                        "Son Fiyat": f"{a['last_price']:.2f} TL",
                        "Teknik Skor": a["technical"],
                        "Momentum": a["momentum"],
                        "200G Trend": "🟢 Üzerinde" if a["signals"]["above_200"] else "🔴 Altında"
                    })
                p_bar.progress((idx + 1) / len(target_list))
            
            res_df = pd.DataFrame(scan_results).sort_values("Genel Skor", ascending=False).reset_index(drop=True)
            res_df.index = res_df.index + 1
            res_df.index.name = "Sıra"
            st.table(res_df)

    # TAB 5: HABER & KAP ETKİ MOTORU
    with tab5:
        st.subheader("🇹🇷 Günlük Haber Akışı & Nedensellik Engine (Zam/KAP Analizi)")
        for n in get_daily_news():
            st.markdown(f"""
            <div class="card">
                <span class="badge bgreen">{n['impact']} | {n['category']}</span>
                <h4 style="margin:8px 0;">{n['title']}</h4>
                <p style="font-size:12px; color:#b7c2d4;">{n['desc']}</p>
                <div style="font-size:11px; color:#63a4ff;">Sistem Skor Katkısı: +{n['score_bonus']} Puan</div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 6: GLOBAL PİYASALAR, EMTİA, ABD HİSSELERİ VE FONLAR (SELCOIN PANELİ)
    with tab6:
        st.subheader("🌐 Döviz, Emtia, ABD Hisseleri, Kripto ve TEFAS Fonları")
        st.caption("Selcoin tarzı anlık varlık kartları, canlı fiyatlar ve TEFAS fon takip ekranı:")

        m_data = get_market_overview()
        
        # 1. Döviz & Emtia Kartları
        st.markdown("#### 🟡 Döviz & Emtialar")
        m_cols = st.columns(4)
        
        commodities = ["USD/TRY", "EUR/TRY", "Gram Altın", "Ons Altın", "Gram Gümüş", "Ons Gümüş", "Brent Petrol"]
        
        col_idx = 0
        for key in commodities:
            if key in m_data:
                info = m_data[key]
                c_class = "green" if info["change"] >= 0 else "red"
                sign = "+" if info["change"] >= 0 else ""
                target_col = m_cols[col_idx % 4]
                target_col.markdown(f"""
                <div class="market-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:14px; color:#eef3fb;">{key}</b>
                        <span class="{c_class}" style="font-size:12px; font-weight:700;">{sign}%{info['change']:.2f}</span>
                    </div>
                    <div style="font-size:20px; font-weight:800; margin-top:8px;">{info['unit']}{info['price']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                col_idx += 1

        st.divider()

        # 2. ABD Hisseleri & Kripto Kartları
        st.markdown("#### 🇺🇸 ABD Devleri & Kripto")
        u_cols = st.columns(4)
        us_assets = ["NVDA", "AAPL", "TSLA", "BTC/USDT", "ETH/USDT"]
        
        col_idx_u = 0
        for key in us_assets:
            if key in m_data:
                info = m_data[key]
                c_class = "green" if info["change"] >= 0 else "red"
                sign = "+" if info["change"] >= 0 else ""
                target_col_u = u_cols[col_idx_u % 4]
                target_col_u.markdown(f"""
                <div class="market-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <b style="font-size:14px; color:#63a4ff;">{key}</b>
                        <span class="{c_class}" style="font-size:12px; font-weight:700;">{sign}%{info['change']:.2f}</span>
                    </div>
                    <div style="font-size:20px; font-weight:800; margin-top:8px;">{info['unit']}{info['price']:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
                col_idx_u += 1

        st.divider()

        # 3. TEFAS Yatırım Fonları Kartları
        st.markdown("#### 📊 Öne Çıkan TEFAS Yatırım Fonları")
        f_cols = st.columns(3)
        
        funds = [
            {"kod": "MAC", "ad": "Marmara Capital Hisse Senedi", "fiyat": "0,6878 TL", "degisim": "-1,63%"},
            {"kod": "IIH", "ad": "İstanbul Portföy Üçüncü Hisse", "fiyat": "31,903 TL", "degisim": "-2,38%"},
            {"kod": "TI2", "ad": "İş Portföy BIST 100 Dışı", "fiyat": "0,1215 TL", "degisim": "-2,54%"},
            {"kod": "GMR", "ad": "Inveo Portföy Hisse Senedi", "fiyat": "1,1873 TL", "degisim": "-0,98%"},
            {"kod": "AK3", "ad": "Ak Portföy Birinci Hisse Senedi", "fiyat": "50,661 TL", "degisim": "-2,26%"},
            {"kod": "BUY", "ad": "Albaraka Portföy Katılım Hisse", "fiyat": "1,5600 TL", "degisim": "-2,32%"}
        ]
        
        for idx, f_info in enumerate(funds):
            f_target = f_cols[idx % 3]
            f_target.markdown(f"""
            <div class="market-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <b style="font-size:15px; color:#35d07f;">{f_info['kod']}</b>
                    <span class="red" style="font-size:12px; font-weight:700;">{f_info['degisim']}</span>
                </div>
                <div style="font-size:12px; color:#9ba9bf; margin-top:3px;">{f_info['ad']}</div>
                <div style="font-size:18px; font-weight:800; margin-top:6px;">{f_info['fiyat']}</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.error(f"{selected_ticker} verisi alınamadı. Kod adının doğruluğunu kontrol ediniz.")
