import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- ڕێکخستنی لاپەڕە ---
st.set_page_config(page_title="گەیاندنی کەرکوک 🚚", layout="wide", initial_sidebar_state="expanded")

# --- ستایلی کوردی (RTL) ---
st.markdown("""
    <style>
    .stApp { direction: rtl; text-align: right; }
    div[data-testid="stForm"] { direction: rtl; }
    </style>
    """, unsafe_allow_html=True)

# --- لای لایە (Sidebar) بۆ ناوی ئێوە ---
st.sidebar.title("🏢 بەڕێوەبەرایەتی")
st.sidebar.subheader("خاوەن کار:")
st.sidebar.write("🧪 خوێندکاری شیکاری")
st.sidebar.subheader("بەرپرسی گەیاندن:")
st.sidebar.write("🚗 کاک عەلی")
st.sidebar.divider()
st.sidebar.info("ئەم ئەپڵیکەیشنە تایبەتە بە بەڕێوەبردنی وەسڵەکانی کەرکوک.")

# --- بنکەی داتا لە میمۆریدا ---
if 'deliveries' not in st.session_state:
    st.session_state.deliveries = []

st.title("📍 سیستەمی گەیاندنی زیرەکی کەرکوک")

# --- بەشی داخڵکردنی وەسڵ (بۆ تۆ) ---
with st.expander("➕ تۆمارکردنی وەسڵی نوێ"):
    with st.form("add_delivery"):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("ناوی کڕیار")
            shop = st.text_input("ناوی دوکان")
            price = st.number_input("نرخی کاڵا (دینار)", value=0, step=1000)
        with col2:
            phone = st.text_input("ژمارەی مۆبایل")
            # پۆتانەکانی ناوەندی کەرکوک وەک دیفۆڵت
            lat = st.number_input("هێڵی پان (Latitude)", format="%.6f", value=35.4676)
            lon = st.number_input("هێڵی درێژ (Longitude)", format="%.6f", value=44.3921)
        
        submit = st.form_submit_button("تۆمارکردن لە لیستی کاک عەلی ✅")
        
        if submit:
            st.session_state.deliveries.append({
                "کڕیار": customer,
                "دوکان": shop,
                "مۆبایل": phone,
                "نرخ": price,
                "lat": lat,
                "lon": lon
            })
            st.success(f"وەسڵی {customer} بە سەرکەوتوویی بۆ کاک عەلی ناردرا!")

# --- نەخشە و لیست (بۆ کاک عەلی) ---
if st.session_state.deliveries:
    st.subheader("🗺 نەخشەی گەیاندن (کاک عەلی سەیری ئێرە بکە)")
    
    # دروستکردنی نەخشە
    m = folium.Map(location=[35.4676, 44.3921], zoom_start=13)
    
    for d in st.session_state.deliveries:
        folium.Marker(
            [d['lat'], d['lon']],
            popup=f"کڕیار: {d['کڕیار']}\nدوکان: {d['دوکان']}\nنرخ: {d['نرخ']:,}",
            tooltip=f"وەسڵی {d['کڕیار']}",
            icon=folium.Icon(color='red', icon='car', prefix='fa')
        ).add_to(m)
    
    # پیشاندانی نەخشەکە
    st_folium(m, width="100%", height=500)

    # خشتەی وەسڵەکان
    st.subheader("📋 لیستی وەسڵەکان")
    df = pd.DataFrame(st.session_state.deliveries)
    st.dataframe(df[["کڕیار", "دوکان", "مۆبایل", "نرخ"]], use_container_width=True)
    
    if st.button("پاککردنەوەی هەموو وەسڵەکان 🗑️"):
        st.session_state.deliveries = []
        st.rerun()
else:
    st.info("کاک عەلی گیان، هێشتا هیچ وەسڵێک تۆمار نەکراوە بۆ ئەمڕۆ.")
