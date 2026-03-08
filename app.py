import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import requests

# ---------- Configuration ----------
ORS_API_KEY = "YOUR_OPENROUTESERVICE_API_KEY"  # Replace with your OpenRouteService API key

st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

# ---------- Sidebar ----------
with st.sidebar:
    st.title("📦 Delivery System - Kirkuk")
    st.info("GPS + Route line + Auto zoom")

# ---------- Database ----------
if "deliveries" not in st.session_state:
    st.session_state.deliveries = []

st.title("📍 Delivery Map with Real-Time GPS")

# ---------- Add delivery ----------
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

# ---------- Map ----------
st.subheader("🗺 Map with Current Location & Routes")

# Default center Kirkuk
map_center = [35.4676, 44.3921]
m = folium.Map(location=map_center, zoom_start=13, tiles="OpenStreetMap")

# ---------- Get current location ----------
st.write("📌 کرتە بکە لە Map بۆ شوێنی ئێوە یا بە موبایل GPS فعاله دەکات.")
clicked = st_folium(folium.Map(location=map_center, zoom_start=13), returned_objects=["last_clicked"])
if clicked and clicked["last_clicked"]:
    lat_current = clicked["last_clicked"]["lat"]
    lon_current = clicked["last_clicked"]["lng"]
else:
    # Default if not clicked yet
    lat_current = 35.4676
    lon_current = 44.3921

# Current location marker
folium.Marker(
    [lat_current, lon_current],
    tooltip="Current Location",
    icon=folium.Icon(color="blue", icon="user", prefix="fa")
).add_to(m)

# Fit bounds list
bounds = [[lat_current, lon_current]]

# ---------- Delivery markers and routes ----------
for d in st.session_state.deliveries:
    dest = [d["lat"], d["lon"]]
    bounds.append(dest)
    
    # Marker
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
    
    # Route line via OpenRouteService API
    coords = [[lon_current, lat_current], [d["lon"], d["lat"]]]
    headers = {
        "Authorization": ORS_API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": coords,
        "format": "geojson"
    }
    try:
        res = requests.post("https://api.openrouteservice.org/v2/directions/driving-car/geojson", json=body, headers=headers)
        if res.status_code == 200:
            geojson = res.json()
            folium.GeoJson(geojson, name="route").add_to(m)
    except Exception as e:
        st.error(f"Route API error: {e}")

# Auto zoom / fit bounds
m.fit_bounds(bounds)

st_folium(m, height=600, width=900)

# Delivery list
st.subheader("📋 Delivery List")
if st.session_state.deliveries:
    df = pd.DataFrame(st.session_state.deliveries)
    st.dataframe(df, use_container_width=True)
else:
    st.info("هێشتا هیچ وەسڵێک تۆمار نەکراوە")

# Clear button
if st.button("🗑 پاککردنەوەی هەموو وەسڵەکان"):
    st.session_state.deliveries = []
    st.experimental_rerun()
