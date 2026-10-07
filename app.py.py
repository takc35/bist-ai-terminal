from analysis_engine import analyze
from data_fetcher import fetch_bist_ticker
from news_engine import get_daily_news
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

st.set_page_config(page_title="TUNA BIST AI TERMINAL", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { background-color: #0b1020; color: #eef3fb; }
    .stMetric { background-color: #121a2b; border: 1px solid #26344e; border-radius: 10px; padding: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("🧠 TUNA BIST AI TERMINAL V0.3")
st.caption("Canlı BIST Verisi + Otomatik Tarayıcı + Türkiye Haber & KAP Motoru")

st.sidebar.header("🔍 Hisse & Radar Seçimi")
selected_ticker = st.sidebar.text_input("BIST Hisse Kodu", value="TUPRS").upper()

bist_100_sample = ["TUPRS", "THYAO", "AKBNK", "GARAN", "ASELS", "EREGL", "SAHOL", "KCHOL", "BIMAS", "SISE"]

tab1, tab2, tab3 = st.tabs(["📊 Tekil Hisse Analizi", "🚀 BIST Otomatik Tarama", "📰 Türkiye Haber & Makro Engine"])

with tab1:
    with st.spinner(f"{selected_ticker} verisi yükleniyor..."):
        df = fetch_bist_ticker(selected_ticker)
        
    if df is not None:
        res = analyze(df)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Son Fiyat", f"{res['last_price']:.2f} TL", f"%{res['change_pct']:.2f}")
        col2.metric("GENEL SKOR", f"{res['total']} / 100", "POZİTİF" if res['total'] >= 75 else "NÖTR")
        col3.metric("Teknik Skor", f"{res['technical']} / 100")
        col4.metric("Momentum", f"{res['momentum']} / 100")
        col5.metric("Trend", f"{res['trend']} / 100")
        
        st.divider()
        g_col, d_col = st.columns([2, 1])
        
        with g_col:
            st.subheader(f"{selected_ticker} Fiyat ve Hareketli Ortalamalar")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], mode='lines', name='Fiyat', line=dict(color='#63a4ff', width=2)))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA50'], mode='lines', name='SMA 50', line=dict(color='#f6c85f', width=1)))
            fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA200'], mode='lines', name='SMA 200', line=dict(color='#35d07f', width=1.5)))
            fig.update_layout(template="plotly_dark", height=400, margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(fig, use_container_width=True)
            
        with d_col:
            st.subheader("🎯 Seviyeler & Sinyaller")
            st.write(f"**Destek Seviyesi:** {res['support']:.2f} TL")
            st.write(f"**Direnç Seviyesi:** {res['resistance']:.2f} TL")
            st.divider()
            st.write("**Teknik Sinyaller:**")
            for k, v in res['signals'].items():
                status = "🟢 EVET" if v else "⚪ HAYIR"
                st.write(f"- {k.replace('_', ' ').title()}: {status}")

        st.divider()
        st.subheader("🤖 AI Karar Özeti")
        st.info(f"**{selected_ticker}** genel analizde **{res['total']}/100** puan aldı. "
                f"Fiyatın 200 günlük ortalamaya olan mesafesi ve momentum yapısı teknik görünümü destekliyor. "
                f"Kısa vadede **{res['support']:.2f} TL** desteği takip edilmeli, **{res['resistance']:.2f} TL** üzerindeki kapanışlar trendi hızlandırabilir.")
    else:
        st.error(f"{selected_ticker} kodu için canlı veri alınamadı. Kodun doğruluğunu kontrol edin.")

with tab2:
    st.subheader("🔥 BIST Örnek Radar & Fırsat Taraması")
    st.caption("BIST hisselerinin teknik, momentum ve temel skor sıralaması:")
    
    if st.button("Taramayı Başlat"):
        scan_results = []
        progress_bar = st.progress(0)
        
        for idx, ticker in enumerate(bist_100_sample):
            ticker_df = fetch_bist_ticker(ticker)
            if ticker_df is not None:
                a = analyze(ticker_df)
                scan_results.append({
                    "Hisse": ticker,
                    "Genel Skor": a["total"],
                    "Fiyat": f"{a['last_price']:.2f} TL",
                    "Teknik": a["technical"],
                    "Momentum": a["momentum"],
                    "200G Üstü": "🟢" if a["signals"]["above_200"] else "🔴",
                    "20G Breakout": "🟢" if a["signals"]["breakout_20"] else "⚪"
                })
            progress_bar.progress((idx + 1) / len(bist_100_sample))
            
        scan_df = pd.DataFrame(scan_results).sort_values("Genel Skor", ascending=False)
        st.dataframe(scan_df, use_container_width=True)

with tab3:
    st.subheader("🇹🇷 Günlük Türkiye Makro & KAP Haber Akışı")
    news_list = get_daily_news()
    for n in news_list:
        with st.expander(f"{n['impact']} | {n['title']} ({n['category']})"):
            st.write(n["desc"])
            st.caption(f"Skor Etkisi: +{n['score_bonus']} puan")