# TAB 2: MODEL PORTFÖYLER (BIST 100 VE BIST TÜM AYRIŞTIRILDI)
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
