st.markdown(f"""
<div class="card" style="border-left: 4px solid #35d07f;">
    <h3 style="margin-top:0;">📌 Neden Listede / Değerlendirme — {selected_ticker}</h3>
    <b style="color:#63a4ff; font-size:15px;">{det_data['reason_title']}</b>
    <p style="color:#b7c2d4; font-size:13px; margin-top:4px;">{det_data['reason_desc']}</p>
    
    <h4 style="color:#f6c85f; margin:15px 0 5px 0;">📊 Teknik Görünüm:</h4>
    <ul style="font-size:13px; color:#c7d2e4; padding-left:20px; margin-top:0;">
""", unsafe_allow_html=True)

for t_b in det_data['tech_bullets']:
    st.markdown(f"<li>{t_b}</li>", unsafe_allow_html=True)
    
st.markdown("""
    </ul>
    <h4 style="color:#35d07f; margin:15px 0 5px 0;">💪 Temel Güçlü Yönler:</h4>
    <ul style="font-size:13px; color:#c7d2e4; padding-left:20px; margin-top:0;">
""", unsafe_allow_html=True)

for f_b in det_data['fund_bullets']:
    st.markdown(f"<li>{f_b}</li>", unsafe_allow_html=True)
    
st.markdown("</ul></div>", unsafe_allow_html=True)
