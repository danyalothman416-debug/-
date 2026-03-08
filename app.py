import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import urllib.parse

# Page config
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

# Sidebar
with st.sidebar:
    st.title("📦 سیستەمی گەیاندنی کەرکوک")
    st.info("سیستەمی زیرەکی گەیاندنی وەسڵەکان لە کەرکوک")

# Database
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

# Title
st.title("📦 سیستەمی گەیاندنی کەرکوک")

# Add Delivery
with st.expander("➕ زیادکردنی وەسڵ"):

    with st.form("delivery_form"):
        col1, col2 = st.columns(2)

        with col1:
            customer = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخی کاڵا", min_value=0)

        with col2:
            phone = st.text_input("ژمارەی مۆبایل")
            lat = st.number_input("Latitude", value=35.4676, format="%.6f")
            lon = st.number_input("Longitude", value=44.3921, format="%.6f")

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

# Map
if st.session_state.deliveries:

    st.subheader("🗺 نەخشەی گەیاندن (کەرکوک)")

    m = folium.Map(location=[35.4676,44.3921], zoom_start=13, tiles="OpenStreetMap")

    for d in st.session_state.deliveries:
        # Google Maps Link
        query = urllib.parse.quote(f"{d['lat']},{d['lon']}")
        gmaps_url = f"https://www.google.com/maps/dir/?api=1&destination={query}"

        folium.Marker(
            [d["lat"], d["lon"]],
            popup=f"""
            کڕیار: {d['کڕیار']} <br>
            دوکان: {d['دوکان']} <br>
            نرخ: {d['نرخ']} <br>
            <a href="{gmaps_url}" target="_blank">🔗 لێرە کرتە بکە بۆ ڕێگای گەیاندن</a>
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
