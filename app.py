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
                    <h3 style
