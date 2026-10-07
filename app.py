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
