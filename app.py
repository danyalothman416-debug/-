import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ---------- ڕێکخستنی لاپەڕە ----------
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

# ---------- Sidebar ----------
with st.sidebar:
    st.title("📦 سیستەمی گەیاندنی کەرکوک")
    st.info("سیستەمی زیرەکی گەیاندنی وەسڵەکان لە کەرکوک")

# ---------- بنکەی داتا ----------
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

# ---------- سەردێڕ ----------
st.title("📦 سیستەمی گەیاندنی کەرکوک")

# ---------- زیادکردنی وەسڵ ----------
with st.expander("➕ زیادکردنی وەسڵ"):

    with st.form("delivery_form"):

        col1, col2 = st.columns(2)

        with col1:
            customer = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخی کاڵا", min_value=0)

        with col2:
            phone = st.text_input("ژمارەی مۆبایل")

            st.markdown("**لە ماپەکە کلیک بکە بۆ دیاری کردنی شوێن**")
            
            # دروستکردنی Map بۆ کلیک
            m_select = folium.Map(location=[35.4676,44.3921], zoom_start=13)

            # Marker پێشتر
            if 'click_location' in st.session_state:
                folium.Marker(
                    st.session_state.click_location,
                    tooltip="شوێنی دیاری کراو",
                    icon=folium.Icon(color='blue', icon='map-marker', prefix='fa')
                ).add_to(m_select)

            # نمایش Map و گرتنی کلیک
            map_data = st_folium(m_select, height=300, width=500, returned_objects=["last_clicked"])

            if map_data and map_data["last_clicked"]:
                lat = map_data["last_clicked"]["lat"]
                lon = map_data["last_clicked"]["lng"]
                st.session_state.click_location = (lat, lon)
            else:
                lat = 35.4676
                lon = 44.3921

        submit = st.form_submit_button("زیادکردنی وەسڵ")

        if submit:
            st.session_state.deliveries.append({
                "کڕیار": customer,
                "دوکان": shop,
                "مۆبایل": phone,
                "نرخ": price,
                "lat": lat,
                "lon": lon
            })
            st.success("وەسڵ بە سەرکەوتوویی زیادکرا ✅")

# ---------- Map ----------
if st.session_state.deliveries:

    st.subheader("🗺 نەخشەی گەیاندن (کەرکوک)")

    m = folium.Map(location=[35.4676,44.3921], zoom_start=13, tiles="OpenStreetMap")

    for d in st.session_state.deliveries:
        folium.Marker(
            [d["lat"], d["lon"]],
            popup=f"""
            کڕیار: {d['کڕیار']} <br>
            دوکان: {d['دوکان']} <br>
            نرخ: {d['نرخ']}
            """,
            tooltip=d["کڕیار"],
            icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
        ).add_to(m)

    st_folium(m, height=500, width=900)

    st.subheader("📋 لیستی وەسڵەکان")
    df = pd.DataFrame(st.session_state.deliveries)
    st.dataframe(df, use_container_width=True)

    if st.button("🗑 پاککردنەوەی هەموو وەسڵەکان"):
        st.session_state.deliveries = []
        st.experimental_rerun()

else:
    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")
