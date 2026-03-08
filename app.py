import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# --- 1. ڕێکخستنی سەرەکی و ستایلی کوردی ---
st.set_page_config(page_title="سیستەمی گەیاندنی کەرکوک", layout="wide")

# ڕێکخستنی شۆێن و زمان بۆ ئەوەی ڕاست بۆ چەپ بێت (RTL)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700&display=swap');
    html, body, [data-testid="stAppViewContainer"], .stTextInput, .stNumberInput, .stButton {
        direction: rtl;
        text-align: right;
        font-family: 'Vazirmatn', sans-serif;
    }
    div[data-testid="stExpander"] div[role="button"] p {
        text-align: right;
    }
    </style>
    """, unsafe_allow_html=True)

ADMIN_PASSWORD = "dr_danyal_2024" 
DB_FILE = "global_deliveries.csv"

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"])

def save_data(df):
    df.to_csv(DB_FILE, index=False)

# --- 2. فۆرمی وەسڵ (ناچارکردنی پڕکردنەوە) ---
st.title("📦 فۆرمی تۆمارکردنی وەسڵ")
st.subheader("تکایە هەموو خانەکان بە جوانی پڕ بکەرەوە")

with st.form("delivery_form", clear_on_submit=True):
    col1, col2 = st.columns(2)
    with col1:
        customer = st.text_input("ناوی کڕیار / اسم الزبون")
        shop = st.text_input("ناوی دوکان / اسم المحل")
        price = st.number_input("نرخی کاڵا (دینار) / سعر البضاعة", min_value=0, step=250)
    with col2:
        phone = st.text_input("ژمارەی مۆبایل / رقم الهاتف")
        address = st.text_input("ناونیشانی ورد / العنوان بالتفصيل")
    
    submit = st.form_submit_button("ناردنی وەسڵ ✅")
    
    if submit:
        # پشکنینی ئەوەی ئایا هەموو خانەکان پڕ کراونەتەوە؟
        if not customer or not shop or not phone or not address or price == 0:
            st.error("⚠️ تکایە هەموو خانەکان پڕ بکەرەوە پێش ناردن! / يرجى ملء جميع الحقول!")
        else:
            current_df = load_data()
            new_row = pd.DataFrame([{
                "کڕیار": customer, 
                "دوکان": shop, 
                "مۆبایل": phone, 
                "نرخ": price, 
                "ناونیشان": address
            }])
            updated_df = pd.concat([current_df, new_row], ignore_index=True)
            save_data(updated_df)
            st.success("✅ وەسڵەکەت بە سەرکەوتوویی تۆمارکرا / تم تسجيل الوصل بنجاح")

st.markdown("---")

# --- 3. بەشی بەڕێوەبەر (شاردراوە) ---
with st.sidebar:
    st.markdown("### ڕێکخستن")
    password = st.text_input("کۆدی چوونەژوورەوە:", type="password")

if password == ADMIN_PASSWORD:
    st.header("👨‍⚕️ داتاکانی بەڕێوەبەر")
    df_to_show = load_data()
    
    if not df_to_show.empty:
        # نەخشە
        map_center = [35.4676, 44.3921]
        m = folium.Map(location=map_center, zoom_start=12)
        for _, row in df_to_show.iterrows():
            folium.Marker(
                location=map_center,
                popup=f"کڕیار: {row['کڕیار']}<br>نرخ: {row['نرخ']}",
                icon=folium.Icon(color="red")
            ).add_to(m)
        st_folium(m, height=400, width=None)

        # خشتەی داتاکان
        st.write("### لیستی وەسڵەکان")
        st.dataframe(df_to_show, use_container_width=True)
        
        # کۆی گشتی پارە
        total_price = df_to_show["نرخ"].sum()
        st.info(f"💰 کۆی گشتی پارە: {total_price:,} دینار")
        
        if st.button("🗑 سڕینەوەی هەموو لیستەکە"):
            save_data(pd.DataFrame(columns=["کڕیار", "دوکان", "مۆبایل", "نرخ", "ناونیشان"]))
            st.rerun()
    else:
        st.write("هیچ وەسڵێک لە لیستدا نییە.")
