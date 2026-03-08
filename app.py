import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ڕێکخستنی لاپەڕە
st.set_page_config(page_title="گەیاندنی کەرکوک 🚚", layout="wide")

# ناوی ئێوە وەک خاوەن بزنس
st.sidebar.title("🛠 بەڕێوەبەران")
st.sidebar.info(f"خاوەن کار: **خوێندکاری شیکاری**\n\nبەرپرسی گەیاندن: **کاک عەلی**")

st.title("📍 سیستەمی گەیاندنی زیرەکی کەرکوک")

# لیستێک بۆ پاشەکەوتکردنی وەسڵەکان
if 'deliveries' not in st.session_state:
    st.session_state.deliveries = []

# --- بەشی داخڵکردنی وەسڵ ---
with st.expander("📝 تۆمارکردنی وەسڵی نوێ (بۆ کاک عەلی)"):
    with st.form("main_form"):
        col1, col2 = st.columns(2)
        with col1:
            c_name = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخی کاڵا", value=0)
        with col2:
            # لێرەدا دەبێت پۆتانەکان (Coordinates) دابنێیت
            # دەتوانیت لە گۆگڵ ماپەوە وەری بگریت (بۆ نموونە: 35.46, 44.39)
            lat = st.number_input("هێڵی پان (Latitude)", format="%.6f", value=35.4676)
            lon = st.number_input("هێڵی درێژ (Longitude)", format="%.6f", value=44.3921)
            phone = st.text_input("ژمارەی مۆبایل")
        
        btn = st.form_submit_button("تۆمارکردن ✅")
        if btn:
            st.session_state.deliveries.append({
                "کڕیار": c_name, "دوکان": shop, "نرخ": price,
                "lat": lat, "lon": lon, "مۆبایل": phone
            })

# --- بەشی نەخشە و لیست (بۆ کاک عەلی) ---
st.subheader("🗺 نەخشەی وەسڵەکان لە کەرکوک")

if st.session_state.deliveries:
    # دروستکردنی نەخشەکە لەسەر سێنتەری کەرکوک
    m = folium.Map(location=[35.4676, 44.3921], zoom_start=12)
    
    # دانانی نیشانە (Marker) بۆ هەر وەسڵێک
    for d in st.session_state.deliveries:
        folium.Marker(
            [d['lat'], d['lon']],
            popup=f"کڕیار: {d['کڕیار']}\nنرخ: {d['نرخ']}",
            tooltip=d['کڕیار'],
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # پیشاندانی نەخشەکە لە ناو ستریمڵیت
    st_folium(m, width=1200, height=500)

    # پیشاندانی لیستەکە لە خوارەوە
    st.subheader("📋 لیستی وەسڵەکان")
    st.table(pd.DataFrame(st.session_state.deliveries)[["کڕیار", "دوکان", "نرخ", "مۆبایل"]])
else:
    st.info("کاک عەلی گیان، هێشتا وەسڵ نییە بۆ گەیاندن.")
