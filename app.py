import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Page config with title + icon ---
st.set_page_config(
    page_title="سیستەمی گەیاندنی کەرکوک",
    page_icon="🚚",
    layout="wide"
)

# --- Developed by header ---
st.markdown("""
<div style='text-align:center; font-size:18px; color:gray;'>
Developed by Dr. Danyal & Eng. Ali
</div>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("📦 Delivery System - Kirkuk")
    st.info("GPS + Map + Delivery (route line temporarily disabled)")

# --- Database ---
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

st.title("📍 Delivery Map (Debug-ready)")

# --- Add delivery ---
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

# --- Map ---
st.subheader("🗺 Map with Current Location & Delivery Markers")

map_center = [35.4676, 44.3921]
m = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

lat_current = 35.4676
lon_current = 44.3921
folium.Marker(
    [lat_current, lon_current],
    tooltip="Current Location",
    icon=folium.Icon(color="blue", icon="user", prefix="fa")
).add_to(m)

bounds = [[lat_current, lon_current]]

for d in st.session_state.deliveries:
    dest = [d["lat"], d["lon"]]
    bounds.append(dest)
    folium.Marker(
        dest,
        popup=f"""
        کڕیار: {d['کڕیار']} <br>
        دوکان: {d['دوکان']} <br>
        نرخ: {d['نرخ']}
        """,
        tooltip=d["کڕیار"],
        icon=folium.Icon(color="red", icon="shopping-cart", prefix="fa")
    ).add_to(m)

m.fit_bounds(bounds)
st_folium(m, height=600, width=900)

# --- Delivery list ---
st.subheader("📋 Delivery List")
if st.session_state.deliveries:
    df = pd.DataFrame(st.session_state.deliveries)
    st.dataframe(df, use_container_width=True)
else:
    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")

# --- Clear button ---
if st.button("🗑 پاککردنەوەی هەموو وەسڵەکان"):
    st.session_state.deliveries = []
    st.success("هەموو وەسڵەکان پاککران ✅")
