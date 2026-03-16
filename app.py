last_order['area']}"
    wa_url = f"https://wa.me/9647801352003?text={urllib.parse.quote(msg)}"
    st.markdown(f'<a href="{wa_url}" target="_blank"><button style="width:100%; background:#25D366; color:white; border:none; padding:15px; border-radius:10px; cursor:pointer; font-weight:bold; margin-bottom:20px;">{L["wa_btn"]}</button></a>', unsafe_allow_html=True)
    if st.button("Reset Form 🔄"):
        st.session_state.submitted = False
        st.rerun()

# --- ٦. بەشی بەدواداچوون ---
st.markdown(f'<div style="background:{card_bg}; padding:20px; border-radius:15px; border:1px solid #D4AF37; margin-top:30px;"><h3>{L["track_title"]}</h3>', unsafe_allow_html=True)
track_phone = st.text_input(f"{L['phone']}", key="track_input")
if st.button(L['track_btn']):
    df_track = load_data()
    res = df_track[df_track['phone'] == track_phone].tail(1)
    if not res.empty: st.success(f"📍 {res.iloc[0]['customer']} | Status: **{res.iloc[0]['status']}**")
    else: st.warning("No order found")
st.markdown('</div>', unsafe_allow_html=True)

# --- ٧. پانێڵی ئەدمین ---
if st.query_params.get("role") == "boss":
    st.divider()
    if st.text_input(L['admin_pass'], type="password") == "golden2024":
        data = load_data()
        
        # --- نەخشەی زیرەک ---
        st.markdown("### 🗺️ Kirkuk Delivery Map")
        m = folium.Map(location=[35.4687, 44.3925], zoom_start=12)
        
        for i, row in data.iterrows():
            if row['area'] in AREA_COORDS:
                lat, lon = AREA_COORDS[row['area']]
                color = "green" if row['status'] in [L['status_delivered'], "✅ گەیشت", "✅ تم التوصيل"] else "orange" if row['status'] in [L['status_onway'], "🚚 لە ڕێگەیە"] else "red"
                
                g_maps = f"https://www.google.com/maps?q={lat},{lon}"
                popup_html = f"<b>{row['customer']}</b><br>{row['area']}<br><a href='{g_maps}' target='_blank'>Open GPS</a>"
                
                folium.Marker([lat, lon], popup=folium.Popup(popup_html, max_width=200), icon=folium.Icon(color=color)).add_to(m)
        
        st_folium(m, width="100%", height=500, key="main_map")

        # --- گرافیکەکان ---
        if not data.empty:
            c1, c2 = st.columns(2)
            with c1: st.plotly_chart(px.pie(data, names='area', title='Areas', color_discrete_sequence=["#D4AF37", "#FFD700"]), use_container_width=True)
            with c2: st.plotly_chart(px.bar(data, x='status', title='Status', color='status'), use_container_width=True)
            st.dataframe(data, use_container_width=True)

# --- ٨. فووتەر ---
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown('<div style="text-align:center; color:#D4AF37; font-size:12px;">Golden Delivery System v1.7.0 | Multi-Language & Map Fix</div>', unsafe_allow_html=True)
