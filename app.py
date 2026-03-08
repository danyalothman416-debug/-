import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- Page config + header ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

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
            address = st.text_input("ناونیشانی کڕیار")  # Replace Lat/Lon with Address
        submit = st.form_submit_button("زیادکردنی وەسڵ")
        if submit:
            st.session_state.deliveries.append({
                "کڕیار": customer,
                "دوکان": shop,
                "مۆبایل": phone,
                "نرخ": price,
                "ناونیشان": address
            })
            st.success("وەسڵ بە سەرکەوتوویی زیادکرا ✅")

# --- Map ---
st.subheader("🗺 Map with Delivery Markers")

# Default map center Kirkuk
map_center = [35.4676, 44.3921]
m = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

# Add delivery markers
bounds = [map_center]
for d in st.session_state.deliveries:
    # For demo: use Kirkuk center for all markers if no Lat/Lon
    dest = map_center
    bounds.append(dest)
    folium.Marker(
        dest,
        popup=f"""
        کڕیار: {d['کڕیار']} <br>
        دوکان: {d['دوکان']} <br>
        نرخ: {d['نرخ']} <br>
        ناونیشان: {d['ناونیشان']}
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
