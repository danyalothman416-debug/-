import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. ڕێکخستنی شاشە ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], .stTextInput, .stNumberInput, .stButton {
        direction: rtl; text-align: right; font-family: 'Vazirmatn', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. تەنها خانەیەکی بەتاڵ لە لای ڕاست (Sidebar) بێ هیچ نووسینێک ---
with st.sidebar:
    # لێرەدا هەموو ناونیشان و ئایکۆنەکانم سڕییەوە
    password = st.text_input("", type="password", placeholder="...")

# --- 3. لاپەڕەی سەرەکی ---
if password == ADMIN_PASSWORD:
    st.header("👨‍⚕️ بەشی بەڕێوەبەر")
    df_to_show = load_data()
    if not df_to_show.empty:
        map_center = [35.4676, 44.3921]
        m = folium.Map(location=map_center, zoom_start=12)
        for _, row in df_to_show.iterrows():
            folium.Marker(location=map_center, popup=f"{row['کڕیار']}").add_to(m)
        st_folium(m, height=450, width=None)
        st.dataframe(df_to_show, use_container_width=True)
        if st.button("🗑 سڕینەوەی لیست"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
else:
    st.title("📦 فۆرمی تۆمارکردنی وەسڵ")
    with st.form("delivery_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            customer = st.text_input("ناوی کڕیار / اسم الزبون")
            shop = st.text_input("ناوی دوکان / اسم المحل")
            price = st.number_input("نرخی کاڵا / سعر البضاعة", min_value=0)
        with col2:
            phone = st.text_input("رقم الهاتف")
            address = st.text_input("العنوان")
        
        if st.form_submit_button("ناردنی وەسڵ ✅"):
            if customer and shop and phone and address:
                df = load_data()
                new_row = pd.DataFrame([{"کڕیار": customer, "دوکان": shop, "مۆبایل": phone, "نرخ": price, "ناونیشان": address}])
                save_data(pd.concat([df, new_row], ignore_index=True))
                st.success("✅ وەسڵەکە نێردرا")
            else:
                st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە")
